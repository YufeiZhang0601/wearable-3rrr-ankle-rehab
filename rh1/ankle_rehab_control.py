"""Shared control utilities for RH1 ankle rehabilitation demos."""

import csv
import math
import os
import xml.etree.ElementTree as ET


XM430_W350_R_STALL_TORQUE_NM = 4.1
XM430_W350_R_NO_LOAD_SPEED_RAD_S = 46.0 * 2.0 * math.pi / 60.0
XM430_POSITION_TICK_DEG = 0.087912
XM430_CENTER_TICK = 2048

ACTUATED_JOINTS = ("joint1", "joint4", "joint6")
PASSIVE_JOINTS = ("joint2", "joint3", "joint5", "joint7")
ALL_DEMO_JOINTS = ACTUATED_JOINTS + PASSIVE_JOINTS
ACTUATOR_PHASES_RAD = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)


def deg_to_rad(value):
    return value * math.pi / 180.0


def rad_to_deg(value):
    return value * 180.0 / math.pi


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def parse_revolute_joint_limits(urdf_path):
    limits = {}
    if not urdf_path or not os.path.exists(urdf_path):
        return limits

    tree = ET.parse(urdf_path)
    root = tree.getroot()

    for joint in root.findall(".//joint"):
        joint_type = joint.attrib.get("type", "")
        if joint_type not in ("revolute", "continuous"):
            continue

        name = joint.attrib.get("name", "")
        if not name or name.startswith("${"):
            continue

        limit = joint.find("limit")
        lower = -math.pi
        upper = math.pi
        effort = 0.0
        velocity = 0.0

        if limit is not None:
            lower = _safe_float(limit.attrib.get("lower"), lower)
            upper = _safe_float(limit.attrib.get("upper"), upper)
            effort = _safe_float(limit.attrib.get("effort"), effort)
            velocity = _safe_float(limit.attrib.get("velocity"), velocity)

        limits[name] = {
            "lower": lower,
            "upper": upper,
            "effort": effort,
            "velocity": velocity,
        }

    return limits


def default_joint_limits():
    limits = {}
    for joint_name in ALL_DEMO_JOINTS:
        limits[joint_name] = {
            "lower": -math.pi,
            "upper": math.pi,
            "effort": XM430_W350_R_STALL_TORQUE_NM,
            "velocity": XM430_W350_R_NO_LOAD_SPEED_RAD_S,
        }
    return limits


def merge_with_default_limits(parsed_limits):
    limits = default_joint_limits()
    for joint_name, joint_limit in parsed_limits.items():
        limits[joint_name] = joint_limit
    return limits


def ankle_rehab_trajectory(t, frequency_hz, dorsi_amp_rad, invert_amp_rad, ramp_time_s):
    phase = 2.0 * math.pi * frequency_hz * t
    if ramp_time_s > 0.0:
        ramp = 0.5 - 0.5 * math.cos(math.pi * clamp(t / ramp_time_s, 0.0, 1.0))
    else:
        ramp = 1.0

    dorsiflexion = ramp * dorsi_amp_rad * math.sin(phase)
    inversion = ramp * invert_amp_rad * math.sin(phase + math.pi / 2.0)
    return dorsiflexion, inversion


def actuator_targets_from_ankle(dorsiflexion, inversion, coupling_gain, limits):
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


def passive_targets_from_actuated(actuated_targets, limits):
    targets = {
        "joint2": -0.50 * actuated_targets["joint1"],
        "joint3": 0.25 * actuated_targets["joint1"],
        "joint5": -0.50 * actuated_targets["joint4"],
        "joint7": -0.50 * actuated_targets["joint6"],
    }
    for joint_name, target in list(targets.items()):
        joint_limit = limits[joint_name]
        targets[joint_name] = clamp(target, joint_limit["lower"], joint_limit["upper"])
    return targets


def position_tick_from_rad(angle_rad):
    ticks = XM430_CENTER_TICK + int(round(rad_to_deg(angle_rad) / XM430_POSITION_TICK_DEG))
    return int(clamp(ticks, 0, 4095))


class AnkleRehabClosedLoopController(object):
    """Small deterministic controller shared by CLI and ROS visualization demos."""

    def __init__(self, limits, config):
        self.limits = merge_with_default_limits(limits)
        self.config = config
        self.torque_limit = min(config["torque_limit_nm"], XM430_W350_R_STALL_TORQUE_NM)
        self.velocity_limit = min(
            config["velocity_limit_rad_s"], XM430_W350_R_NO_LOAD_SPEED_RAD_S
        )
        self.state = {}
        self.integral = {}
        for joint_name in ACTUATED_JOINTS:
            self.state[joint_name] = {"q": 0.0, "dq": 0.0}
            self.integral[joint_name] = 0.0

    def step(self, t, dt):
        ankle_dorsi, ankle_invert = ankle_rehab_trajectory(
            t,
            self.config["frequency_hz"],
            deg_to_rad(self.config["dorsi_amp_deg"]),
            deg_to_rad(self.config["invert_amp_deg"]),
            self.config["ramp_time_s"],
        )
        targets = actuator_targets_from_ankle(
            ankle_dorsi, ankle_invert, self.config["coupling_gain"], self.limits
        )

        row = {
            "time_s": t,
            "ankle_dorsiflexion_deg": rad_to_deg(ankle_dorsi),
            "ankle_inversion_deg": rad_to_deg(ankle_invert),
        }
        measured_positions = {}

        for joint_name in ACTUATED_JOINTS:
            q = self.state[joint_name]["q"]
            dq = self.state[joint_name]["dq"]
            error = targets[joint_name] - q
            self.integral[joint_name] = clamp(
                self.integral[joint_name] + error * dt,
                -self.config["integral_limit"],
                self.config["integral_limit"],
            )

            torque_cmd = (
                self.config["kp"] * error
                - self.config["kd"] * dq
                + self.config["ki"] * self.integral[joint_name]
            )
            torque_cmd = clamp(torque_cmd, -self.torque_limit, self.torque_limit)

            acceleration = (
                torque_cmd - self.config["load_damping"] * dq
            ) / self.config["load_inertia"]
            dq = clamp(dq + acceleration * dt, -self.velocity_limit, self.velocity_limit)
            q = q + dq * dt
            q = clamp(q, self.limits[joint_name]["lower"], self.limits[joint_name]["upper"])

            self.state[joint_name]["q"] = q
            self.state[joint_name]["dq"] = dq
            measured_positions[joint_name] = q

            row["%s_target_deg" % joint_name] = rad_to_deg(targets[joint_name])
            row["%s_measured_deg" % joint_name] = rad_to_deg(q)
            row["%s_error_deg" % joint_name] = rad_to_deg(targets[joint_name] - q)
            row["%s_torque_nm" % joint_name] = torque_cmd
            row["%s_goal_tick" % joint_name] = position_tick_from_rad(targets[joint_name])

        passive_targets = passive_targets_from_actuated(measured_positions, self.limits)
        measured_positions.update(passive_targets)

        return {
            "row": row,
            "positions": measured_positions,
            "actuated_targets": targets,
        }


def default_config():
    return {
        "frequency_hz": 0.05,
        "ramp_time_s": 3.0,
        "dorsi_amp_deg": 12.0,
        "invert_amp_deg": 6.0,
        "coupling_gain": 1.0,
        "kp": 14.0,
        "kd": 0.55,
        "ki": 0.8,
        "integral_limit": 0.15,
        "load_inertia": 0.018,
        "load_damping": 0.08,
        "torque_limit_nm": 1.2,
        "velocity_limit_rad_s": 0.8,
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


def _safe_float(value, default):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
