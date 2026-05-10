#!/usr/bin/env python3
"""Extract kinematic candidates from a SolidWorks STEP assembly.

This script is intentionally dependency-free. It does not replace a real CAD
kernel such as OpenCascade/FreeCAD, but it can mine useful cylindrical-surface
axes from an AP203/AP214/AP242 STEP file and produce a short list of candidate
motor axes and foot-plate connection holes for manual confirmation.
"""

import argparse
import collections
import json
import math
import os
import re


NUMBER_RE = re.compile(
    r"[-+]?\d*\.\d+(?:[EeDd][-+]?\d+)?|[-+]?\d+(?:[EeDd][-+]?\d+)?"
)
REF_RE = re.compile(r"#(\d+)")
STATEMENT_RE = re.compile(r"^#(\d+)\s*=\s*(.*);\s*$")


def parse_step_entities(step_path):
    entities = {}
    buffer = ""

    with open(step_path, "r", encoding="utf-8", errors="ignore") as step_file:
        for line in step_file:
            stripped = line.strip()
            if not stripped:
                continue
            buffer = (buffer + " " + stripped).strip()
            if stripped.endswith(";"):
                match = STATEMENT_RE.match(buffer)
                if match:
                    entities[int(match.group(1))] = match.group(2)
                buffer = ""

    return entities


def refs(statement):
    return [int(value) for value in REF_RE.findall(statement)]


def numbers(statement):
    return [float(value.replace("D", "E").replace("d", "e")) for value in NUMBER_RE.findall(statement)]


def vector_norm(vector):
    return math.sqrt(sum(component * component for component in vector))


def normalize(vector):
    norm = vector_norm(vector)
    if norm == 0.0:
        return tuple(vector)
    return tuple(component / norm for component in vector)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def sub(left, right):
    return tuple(a - b for a, b in zip(left, right))


def distance(left, right):
    return vector_norm(sub(left, right))


class StepGeometry(object):
    def __init__(self, entities):
        self.entities = entities

    def point(self, entity_id):
        statement = self.entities.get(entity_id, "")
        if "CARTESIAN_POINT" not in statement:
            return None
        values = numbers(statement)
        if len(values) < 3:
            return None
        return tuple(values[-3:])

    def direction(self, entity_id):
        statement = self.entities.get(entity_id, "")
        if "DIRECTION" not in statement:
            return None
        values = numbers(statement)
        if len(values) < 3:
            return None
        return normalize(tuple(values[-3:]))

    def axis2_placement(self, entity_id):
        statement = self.entities.get(entity_id, "")
        if "AXIS2_PLACEMENT_3D" not in statement:
            return None
        entity_refs = refs(statement)
        if len(entity_refs) < 3:
            return None
        point = self.point(entity_refs[0])
        axis = self.direction(entity_refs[1])
        ref_direction = self.direction(entity_refs[2])
        if point is None or axis is None:
            return None
        return {
            "point": point,
            "direction": axis,
            "reference_direction": ref_direction,
        }

    def products(self):
        products = []
        for entity_id, statement in self.entities.items():
            if not statement.startswith("PRODUCT"):
                continue
            match = re.search(r"PRODUCT \( '([^']*)'", statement)
            name = match.group(1) if match else ""
            if name:
                products.append({"id": entity_id, "name": name})
        return products

    def cylinders(self):
        cylinders = []
        for entity_id, statement in self.entities.items():
            if not statement.startswith("CYLINDRICAL_SURFACE"):
                continue

            entity_refs = refs(statement)
            values = numbers(statement)
            if not entity_refs or not values:
                continue

            placement = self.axis2_placement(entity_refs[0])
            if not placement:
                continue

            cylinders.append(
                {
                    "id": entity_id,
                    "radius_mm": values[-1],
                    "point_mm": placement["point"],
                    "direction": placement["direction"],
                }
            )
        return cylinders


def canonical_direction(direction):
    """Make opposite directions comparable."""
    for component in direction:
        if abs(component) < 1e-9:
            continue
        if component < 0:
            return tuple(-value for value in direction)
        return tuple(direction)
    return tuple(direction)


def cluster_cylinders(cylinders, radius_tolerance_mm, distance_tolerance_mm, angle_tolerance_deg):
    clusters = []
    cos_tolerance = math.cos(math.radians(angle_tolerance_deg))

    for cylinder in sorted(cylinders, key=lambda item: (round(item["radius_mm"], 3), item["id"])):
        direction = canonical_direction(cylinder["direction"])
        assigned = False

        for cluster in clusters:
            if abs(cluster["radius_mm"] - cylinder["radius_mm"]) > radius_tolerance_mm:
                continue
            if abs(dot(cluster["direction"], direction)) < cos_tolerance:
                continue
            if distance(cluster["point_mm"], cylinder["point_mm"]) > distance_tolerance_mm:
                continue

            cluster["members"].append(cylinder)
            count = len(cluster["members"])
            cluster["radius_mm"] = (
                (cluster["radius_mm"] * (count - 1)) + cylinder["radius_mm"]
            ) / count
            cluster["point_mm"] = tuple(
                ((cluster["point_mm"][idx] * (count - 1)) + cylinder["point_mm"][idx]) / count
                for idx in range(3)
            )
            cluster["direction"] = normalize(
                tuple(
                    ((cluster["direction"][idx] * (count - 1)) + direction[idx]) / count
                    for idx in range(3)
                )
            )
            assigned = True
            break

        if not assigned:
            clusters.append(
                {
                    "radius_mm": cylinder["radius_mm"],
                    "point_mm": cylinder["point_mm"],
                    "direction": direction,
                    "members": [cylinder],
                }
            )

    for index, cluster in enumerate(clusters, start=1):
        cluster["cluster_id"] = index
        cluster["count"] = len(cluster["members"])
        cluster["source_surface_ids"] = [member["id"] for member in cluster["members"][:12]]

    return clusters


def score_cluster(cluster):
    radius = cluster["radius_mm"]
    count = cluster["count"]

    score = min(count, 8) * 2.0
    if 3.0 <= radius <= 15.0:
        score += 8.0
    if radius in (4.0, 5.0, 6.0, 8.0, 10.0):
        score += 3.0
    return score


def select_candidates(clusters, radius_min_mm, radius_max_mm, limit):
    filtered = [
        cluster
        for cluster in clusters
        if radius_min_mm <= cluster["radius_mm"] <= radius_max_mm
    ]
    filtered.sort(key=lambda item: (-score_cluster(item), item["radius_mm"], item["cluster_id"]))
    return filtered[:limit]


def rounded_list(values, digits=6):
    return [round(value, digits) for value in values]


def serializable_cluster(cluster):
    return {
        "cluster_id": cluster["cluster_id"],
        "radius_mm": round(cluster["radius_mm"], 6),
        "point_mm": rounded_list(cluster["point_mm"]),
        "direction": rounded_list(cluster["direction"]),
        "count": cluster["count"],
        "source_surface_ids": cluster["source_surface_ids"],
    }


def write_markdown(report_path, payload):
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write("# STEP Kinematic Candidate Report\n\n")
        report_file.write("This report is generated from STEP cylindrical surfaces. ")
        report_file.write("Confirm the selected motor axes and foot-plate connection holes in CAD before using them for IK.\n\n")

        report_file.write("## Products\n\n")
        for product in payload["products"]:
            report_file.write("- `#{}` `{}`\n".format(product["id"], product["name"]))

        report_file.write("\n## Radius Histogram\n\n")
        for radius, count in payload["radius_histogram"]:
            report_file.write("- radius `{:.3f} mm`: `{}` surfaces\n".format(radius, count))

        report_file.write("\n## Candidate Axis Clusters\n\n")
        for candidate in payload["candidate_axis_clusters"]:
            report_file.write(
                "- cluster `{}`: radius `{:.3f} mm`, count `{}`, point_mm `{}`, direction `{}`\n".format(
                    candidate["cluster_id"],
                    candidate["radius_mm"],
                    candidate["count"],
                    candidate["point_mm"],
                    candidate["direction"],
                )
            )


def build_payload(args):
    entities = parse_step_entities(args.step_file)
    geometry = StepGeometry(entities)
    cylinders = geometry.cylinders()
    clusters = cluster_cylinders(
        cylinders,
        radius_tolerance_mm=args.radius_tolerance_mm,
        distance_tolerance_mm=args.distance_tolerance_mm,
        angle_tolerance_deg=args.angle_tolerance_deg,
    )

    histogram = collections.Counter(round(cylinder["radius_mm"], 3) for cylinder in cylinders)
    histogram_items = sorted(histogram.items(), key=lambda item: (-item[1], item[0]))[:40]
    candidates = select_candidates(
        clusters,
        radius_min_mm=args.radius_min_mm,
        radius_max_mm=args.radius_max_mm,
        limit=args.limit,
    )

    return {
        "source_step": os.path.abspath(args.step_file),
        "notes": [
            "Units appear to be millimeters for this SolidWorks STEP export.",
            "These are geometric candidates, not verified mechanism parameters.",
            "Use CAD or photos to choose the three XM430 output axes and three foot-plate connection axes.",
        ],
        "entity_count": len(entities),
        "cylindrical_surface_count": len(cylinders),
        "cluster_count": len(clusters),
        "products": geometry.products(),
        "radius_histogram": histogram_items,
        "candidate_axis_clusters": [serializable_cluster(cluster) for cluster in candidates],
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract cylindrical-axis candidates from a SolidWorks STEP assembly."
    )
    parser.add_argument("step_file", help="Path to the STEP file exported from SolidWorks.")
    parser.add_argument(
        "--output-json",
        default=os.path.join("demo_output", "step_kinematics_candidates.json"),
        help="JSON report path.",
    )
    parser.add_argument(
        "--output-md",
        default=os.path.join("demo_output", "step_kinematics_candidates.md"),
        help="Markdown report path.",
    )
    parser.add_argument("--limit", type=int, default=80, help="Number of candidate clusters to report.")
    parser.add_argument("--radius-min-mm", type=float, default=3.0)
    parser.add_argument("--radius-max-mm", type=float, default=15.0)
    parser.add_argument("--radius-tolerance-mm", type=float, default=0.05)
    parser.add_argument("--distance-tolerance-mm", type=float, default=0.5)
    parser.add_argument("--angle-tolerance-deg", type=float, default=1.0)
    return parser.parse_args()


def main():
    args = parse_args()
    payload = build_payload(args)

    os.makedirs(os.path.dirname(args.output_json) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.output_md) or ".", exist_ok=True)

    with open(args.output_json, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)
        json_file.write("\n")

    write_markdown(args.output_md, payload)

    print("STEP file:", payload["source_step"])
    print("Products:", len(payload["products"]))
    print("Cylindrical surfaces:", payload["cylindrical_surface_count"])
    print("Axis clusters:", payload["cluster_count"])
    print("Candidate clusters written:", len(payload["candidate_axis_clusters"]))
    print("JSON:", os.path.abspath(args.output_json))
    print("Markdown:", os.path.abspath(args.output_md))


if __name__ == "__main__":
    main()
