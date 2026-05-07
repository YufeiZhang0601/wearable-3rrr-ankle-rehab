#!/usr/bin/env python3
"""Closed-loop ankle rehabilitation demo driven by the rh1 URDF.

This demo is intentionally dependency-free so it can run before Gazebo,
PyBullet, ROS 2 control, or Dynamixel SDK are installed. It parses the URDF,
uses the three base joints as virtual XM430-W350-R actuators, tracks a
human-safe ankle rehab trajectory, and writes the simulated feedback loop to a
CSV file for inspection.
"""

import argparse
import csv
import math
import os
import xml.etree.ElementTree as ET


XM430_W350_R_STALL_TORQUE_NM = 4.1
XM430_W350_R_NO_LOAD_SPEED_RAD_S = 46.0 * 2.0 * math.pi / 60.0
XM430_POSITION_TICK_DEG = 0.087912
XM430_CENTER_TICK = 2048

ACTUATED_JOINTS = ("joint1", "joint4", "joint6")
ACTUATOR_PHASES_RAD = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)


def deg_to_rad(value):
    return value * math.pi / 180.0


def rad_to_deg(value):
    return value * 180.0 / math.pi


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def parse_revolute_joint_limits(urdf_path):
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    limits = {}

    for joint in root.findall("joint"):
        joint_type = joint.attrib.get("type", "")
        if joint_type not in ("revolute", "continuous"):
            continue

        name = joint.attrib["name"]
        limit = joint.find("limit")
        lower = -math.pi
        upper = math.pi
        effort = 0.0
        velocity = 0.0

        if limit is not None:
            lower = float(limit.attrib.get("lower", lower))
            upper = float(limit.attrib.get("upper", upper))
            effort = float(limit.attrib.get("effort", effort))
            velocity = float(limit.attrib.get("velocity", velocity))

        limits[name] = {
            "lower": lower,
            "upper": upper,
            "effort": effort,
            "velocity": velocity,
        }

    return limits


def ankle_rehab_trajectory(t, frequency_hz, dorsi_amp_rad, invert_amp_rad, ramp_time_s):
    """Slow 2-DOF ankle motion inside conservative rehab ROM."""
    phase = 2.0 * math.pi * frequency_hz * t
    if ramp_time_s > 0.0:
        ramp = 0.5 - 0.5 * math.cos(math.pi * clamp(t / ramp_time_s, 0.0, 1.0))
    else:
        ramp = 1.0

    dorsiflexion = ramp * dorsi_amp_rad * math.sin(phase)
    inversion = ramp * invert_amp_rad * math.sin(phase + math.pi / 2.0)
    return dorsiflexion, inversion


def actuator_targets_from_ankle(dorsiflexion, inversion, coupling_gain, limits):
    """Map ankle pitch/roll demand to three equally spaced virtual actuators."""
    targets = {}
    for joint_name, phase in zip(ACTUATED_JOINTS, ACTUATOR_PHASES_RAD):
        raw_target = coupling_gain * (
            dorsiflexion * math.cos(phase) + inversion * math.sin(phase)
        )
        joint_limit = limits[joint_name]
        targets[joint_name] = clamp(
            raw_target, joint_limit["lower"], joint_limit["upper"]
        )
    return targets


def position_tick_from_rad(angle_rad):
    ticks = XM430_CENTER_TICK + int(round(rad_to_deg(angle_rad) / XM430_POSITION_TICK_DEG))
    return int(clamp(ticks, 0, 4095))


def simulate(args):
    urdf_path = os.path.abspath(args.urdf)
    limits = parse_revolute_joint_limits(urdf_path)
    missing = [name for name in ACTUATED_JOINTS if name not in limits]
    if missing:
        raise RuntimeError("URDF is missing actuated joints: %s" % ", ".join(missing))

    torque_limit = min(args.torque_limit_nm, XM430_W350_R_STALL_TORQUE_NM)
    velocity_limit = min(args.velocity_limit_rad_s, XM430_W350_R_NO_LOAD_SPEED_RAD_S)

    state = {}
    integral = {}
    for joint_name in ACTUATED_JOINTS:
        state[joint_name] = {"q": 0.0, "dq": 0.0}
        integral[joint_name] = 0.0

    rows = []
    max_error = 0.0
    sum_sq_error = 0.0
    sample_count = 0
    steps = int(args.duration / args.dt)

    for step in range(steps + 1):
        t = step * args.dt
        ankle_dorsi, ankle_invert = ankle_rehab_trajectory(
            t,
            args.frequency_hz,
            deg_to_rad(args.dorsi_amp_deg),
            deg_to_rad(args.invert_amp_deg),
            args.ramp_time_s,
        )
        targets = actuator_targets_from_ankle(
            ankle_dorsi, ankle_invert, args.coupling_gain, limits
        )

        row = {
            "time_s": t,
            "ankle_dorsiflexion_deg": rad_to_deg(ankle_dorsi),
            "ankle_inversion_deg": rad_to_deg(ankle_invert),
        }

        for joint_name in ACTUATED_JOINTS:
            q = state[joint_name]["q"]
            dq = state[joint_name]["dq"]
            error = targets[joint_name] - q
            integral[joint_name] = clamp(
                integral[joint_name] + error * args.dt,
                -args.integral_limit,
                args.integral_limit,
            )

            torque_cmd = (
                args.kp * error
                - args.kd * dq
                + args.ki * integral[joint_name]
            )
            torque_cmd = clamp(torque_cmd, -torque_limit, torque_limit)

            # Lightweight motor/load model: enough to test controller stability
            # before connecting a real patient-side actuator.
            acceleration = (torque_cmd - args.load_damping * dq) / args.load_inertia
            dq = clamp(dq + acceleration * args.dt, -velocity_limit, velocity_limit)
            q = q + dq * args.dt
            q = clamp(q, limits[joint_name]["lower"], limits[joint_name]["upper"])

            state[joint_name]["q"] = q
            state[joint_name]["dq"] = dq

            abs_error = abs(targets[joint_name] - q)
            max_error = max(max_error, abs_error)
            sum_sq_error += abs_error * abs_error
            sample_count += 1

            row["%s_target_deg" % joint_name] = rad_to_deg(targets[joint_name])
            row["%s_measured_deg" % joint_name] = rad_to_deg(q)
            row["%s_error_deg" % joint_name] = rad_to_deg(targets[joint_name] - q)
            row["%s_torque_nm" % joint_name] = torque_cmd
            row["%s_goal_tick" % joint_name] = position_tick_from_rad(targets[joint_name])

        rows.append(row)

    rms_error = math.sqrt(sum_sq_error / max(1, sample_count))
    return {
        "urdf_path": urdf_path,
        "rows": rows,
        "rms_error_rad": rms_error,
        "max_error_rad": max_error,
        "torque_limit_nm": torque_limit,
        "velocity_limit_rad_s": velocity_limit,
    }


def write_csv(path, rows):
    if not rows:
        return

    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Run a stable closed-loop ankle rehab demo from rh1.urdf."
    )
    parser.add_argument("--urdf", default=os.path.join("urdf", "rh1.urdf"))
    parser.add_argument("--csv", default=os.path.join("demo_output", "ankle_rehab_closed_loop.csv"))
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--frequency-hz", type=float, default=0.05)
    parser.add_argument("--ramp-time-s", type=float, default=3.0)
    parser.add_argument("--dorsi-amp-deg", type=float, default=12.0)
    parser.add_argument("--invert-amp-deg", type=float, default=6.0)
    parser.add_argument("--coupling-gain", type=float, default=1.0)
    parser.add_argument("--kp", type=float, default=14.0)
    parser.add_argument("--kd", type=float, default=0.55)
    parser.add_argument("--ki", type=float, default=0.8)
    parser.add_argument("--integral-limit", type=float, default=0.15)
    parser.add_argument("--load-inertia", type=float, default=0.018)
    parser.add_argument("--load-damping", type=float, default=0.08)
    parser.add_argument("--torque-limit-nm", type=float, default=1.2)
    parser.add_argument("--velocity-limit-rad-s", type=float, default=0.8)
    return parser


def main():
    args = build_arg_parser().parse_args()
    result = simulate(args)
    write_csv(args.csv, result["rows"])

    final_row = result["rows"][-1]
    print("URDF: %s" % result["urdf_path"])
    print("Actuated joints: %s" % ", ".join(ACTUATED_JOINTS))
    print("Trajectory: %.1f deg dorsiflexion/plantarflexion, %.1f deg inversion/eversion at %.3f Hz" % (
        args.dorsi_amp_deg,
        args.invert_amp_deg,
        args.frequency_hz,
    ))
    print("XM430-W350-R limits used: %.2f Nm torque, %.2f rad/s velocity" % (
        result["torque_limit_nm"],
        result["velocity_limit_rad_s"],
    ))
    print("Tracking RMS error: %.3f deg" % rad_to_deg(result["rms_error_rad"]))
    print("Tracking max error: %.3f deg" % rad_to_deg(result["max_error_rad"]))
    print("Final Dynamixel goal ticks:")
    for joint_name in ACTUATED_JOINTS:
        print("  %s: %s" % (joint_name, final_row["%s_goal_tick" % joint_name]))
    print("CSV written to: %s" % os.path.abspath(args.csv))

    if rad_to_deg(result["max_error_rad"]) > 3.0:
        print("WARNING: max error is above 3 deg; reduce speed/amplitude or tune gains before hardware tests.")
    else:
        print("PASS: closed-loop tracking stayed within the 3 deg demo threshold.")


if __name__ == "__main__":
    main()
