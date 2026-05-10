#!/usr/bin/env python3
"""Run the RH1 parallel ankle IK solver for one requested foot-plate pose."""

import argparse
import json
import os
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from rh1.parallel_ik import ParallelAnkleIK, deg_to_rad, load_params_json


def parse_args():
    parser = argparse.ArgumentParser(description="Solve RH1 parallel ankle IK.")
    parser.add_argument("params_json", help="Path to a confirmed IK parameter JSON file.")
    parser.add_argument("--roll-deg", type=float, default=0.0, help="Inversion/eversion angle.")
    parser.add_argument("--pitch-deg", type=float, default=0.0, help="Dorsiflexion/plantarflexion angle.")
    parser.add_argument("--yaw-deg", type=float, default=0.0, help="Internal/external rotation angle.")
    parser.add_argument("--samples", type=int, default=181, help="Grid samples per motor limit range.")
    parser.add_argument("--tolerance-mm", type=float, default=1e-5, help="Allowed leg length residual.")
    return parser.parse_args()


def main():
    args = parse_args()
    params = load_params_json(args.params_json)
    solver = ParallelAnkleIK(params)
    result = solver.solve_orientation(
        roll_rad=deg_to_rad(args.roll_deg),
        pitch_rad=deg_to_rad(args.pitch_deg),
        yaw_rad=deg_to_rad(args.yaw_deg),
        samples=args.samples,
        tolerance_mm=args.tolerance_mm,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
