"""Numerical inverse kinematics for the RH1 spherical parallel ankle mechanism.

The model assumes each actuated leg has one Dynamixel-driven revolute axis and
one effective rigid link between an actuator-side point and a foot-plate point.
For a requested foot-plate orientation, each motor angle is solved from a scalar
distance constraint.
"""

import json
import math


def deg_to_rad(value):
    return value * math.pi / 180.0


def rad_to_deg(value):
    return value * 180.0 / math.pi


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def sub(left, right):
    return tuple(a - b for a, b in zip(left, right))


def scale(vector, factor):
    return tuple(component * factor for component in vector)


def norm(vector):
    return math.sqrt(dot(vector, vector))


def normalize(vector):
    length = norm(vector)
    if length == 0.0:
        raise ValueError("Cannot normalize a zero-length vector.")
    return scale(vector, 1.0 / length)


def mat_vec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def mat_mul(left, right):
    columns = list(zip(*right))
    return tuple(tuple(dot(row, column) for column in columns) for row in left)


def rotation_x(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return ((1.0, 0.0, 0.0), (0.0, c, -s), (0.0, s, c))


def rotation_y(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return ((c, 0.0, s), (0.0, 1.0, 0.0), (-s, 0.0, c))


def rotation_z(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def foot_orientation_from_rpy(roll_rad, pitch_rad, yaw_rad):
    """Return R_base_foot using ZYX yaw-pitch-roll convention."""
    return mat_mul(rotation_z(yaw_rad), mat_mul(rotation_y(pitch_rad), rotation_x(roll_rad)))


def rotate_about_axis(point, axis_point, axis_direction, angle_rad):
    """Rotate a point around an arbitrary axis using Rodrigues' formula."""
    axis = normalize(axis_direction)
    relative = sub(point, axis_point)
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    rotated = add(
        add(scale(relative, c), scale(cross(axis, relative), s)),
        scale(axis, dot(axis, relative) * (1.0 - c)),
    )
    return add(axis_point, rotated)


class LegParameters:
    def __init__(
        self,
        name,
        axis_point_base_mm,
        axis_direction_base,
        horn_point_zero_base_mm,
        foot_point_foot_mm,
        rod_length_mm,
        zero_angle_rad=0.0,
        lower_angle_rad=deg_to_rad(-45.0),
        upper_angle_rad=deg_to_rad(45.0),
        dynamixel_id=0,
    ):
        self.name = name
        self.axis_point_base_mm = axis_point_base_mm
        self.axis_direction_base = axis_direction_base
        self.horn_point_zero_base_mm = horn_point_zero_base_mm
        self.foot_point_foot_mm = foot_point_foot_mm
        self.rod_length_mm = rod_length_mm
        self.zero_angle_rad = zero_angle_rad
        self.lower_angle_rad = lower_angle_rad
        self.upper_angle_rad = upper_angle_rad
        self.dynamixel_id = dynamixel_id


class ParallelIKParameters:
    def __init__(self, ankle_center_base_mm, legs):
        self.ankle_center_base_mm = ankle_center_base_mm
        self.legs = legs


class NoIKSolution(RuntimeError):
    pass


class ParallelAnkleIK(object):
    def __init__(self, params):
        self.params = params

    def solve_orientation(
        self,
        roll_rad,
        pitch_rad,
        yaw_rad=0.0,
        previous_solution=None,
        samples=181,
        tolerance_mm=1e-5,
    ):
        rotation = foot_orientation_from_rpy(roll_rad, pitch_rad, yaw_rad)
        previous_solution = previous_solution or {}
        solution = {}
        residuals = {}

        for leg in self.params.legs:
            foot_point_base = add(
                self.params.ankle_center_base_mm,
                mat_vec(rotation, leg.foot_point_foot_mm),
            )
            preferred = previous_solution.get(leg.name, leg.zero_angle_rad)
            angle, residual = self._solve_leg_angle(
                leg,
                foot_point_base,
                preferred_angle_rad=preferred,
                samples=samples,
                tolerance_mm=tolerance_mm,
            )
            solution[leg.name] = angle
            residuals[leg.name] = residual

        return {
            "joint_angles_rad": solution,
            "joint_angles_deg": {name: rad_to_deg(value) for name, value in solution.items()},
            "residuals_mm": residuals,
        }

    def leg_residual(self, leg, foot_point_base, motor_angle_rad):
        horn_point = rotate_about_axis(
            leg.horn_point_zero_base_mm,
            leg.axis_point_base_mm,
            leg.axis_direction_base,
            motor_angle_rad - leg.zero_angle_rad,
        )
        return norm(sub(foot_point_base, horn_point)) - leg.rod_length_mm

    def _solve_leg_angle(
        self,
        leg,
        foot_point_base,
        preferred_angle_rad,
        samples,
        tolerance_mm,
    ):
        lower = leg.lower_angle_rad
        upper = leg.upper_angle_rad
        if lower >= upper:
            raise ValueError("%s has invalid motor limits." % leg.name)

        sample_count = max(3, samples)
        step = (upper - lower) / float(sample_count - 1)
        grid = [lower + step * index for index in range(sample_count)]
        values = [self.leg_residual(leg, foot_point_base, angle) for angle in grid]

        brackets = []
        best_index = min(range(sample_count), key=lambda idx: abs(values[idx]))
        best_angle = grid[best_index]
        best_residual = values[best_index]

        for index in range(sample_count - 1):
            left_angle = grid[index]
            right_angle = grid[index + 1]
            left_value = values[index]
            right_value = values[index + 1]
            if left_value == 0.0:
                brackets.append((left_angle, left_angle))
            elif left_value * right_value < 0.0:
                brackets.append((left_angle, right_angle))

        roots = []
        for left_angle, right_angle in brackets:
            if left_angle == right_angle:
                root = left_angle
            else:
                root = self._bisect_leg(leg, foot_point_base, left_angle, right_angle, tolerance_mm)
            roots.append(root)

        if roots:
            angle = min(roots, key=lambda candidate: abs(candidate - preferred_angle_rad))
            return angle, self.leg_residual(leg, foot_point_base, angle)

        if abs(best_residual) <= tolerance_mm:
            return best_angle, best_residual

        raise NoIKSolution(
            "%s has no bracketed IK solution; best residual %.6f mm at %.3f deg"
            % (leg.name, best_residual, rad_to_deg(best_angle))
        )

    def _bisect_leg(self, leg, foot_point_base, left_angle, right_angle, tolerance_mm):
        left_value = self.leg_residual(leg, foot_point_base, left_angle)
        right_value = self.leg_residual(leg, foot_point_base, right_angle)

        for _ in range(80):
            middle = 0.5 * (left_angle + right_angle)
            middle_value = self.leg_residual(leg, foot_point_base, middle)
            if abs(middle_value) <= tolerance_mm:
                return middle
            if left_value * middle_value <= 0.0:
                right_angle = middle
                right_value = middle_value
            else:
                left_angle = middle
                left_value = middle_value

            if abs(right_angle - left_angle) <= deg_to_rad(1e-6):
                break

        if abs(left_value) < abs(right_value):
            return left_angle
        return right_angle


def _tuple3(values, field_name):
    if len(values) != 3:
        raise ValueError("%s must contain exactly three numbers." % field_name)
    return tuple(float(value) for value in values)


def load_params_json(path):
    with open(path, "r", encoding="utf-8") as params_file:
        data = json.load(params_file)

    legs = []
    for leg_data in data["legs"]:
        legs.append(
            LegParameters(
                name=leg_data["name"],
                axis_point_base_mm=_tuple3(
                    leg_data["axis_point_base_mm"], "axis_point_base_mm"
                ),
                axis_direction_base=_tuple3(
                    leg_data["axis_direction_base"], "axis_direction_base"
                ),
                horn_point_zero_base_mm=_tuple3(
                    leg_data["horn_point_zero_base_mm"], "horn_point_zero_base_mm"
                ),
                foot_point_foot_mm=_tuple3(
                    leg_data["foot_point_foot_mm"], "foot_point_foot_mm"
                ),
                rod_length_mm=float(leg_data["rod_length_mm"]),
                zero_angle_rad=float(leg_data.get("zero_angle_rad", 0.0)),
                lower_angle_rad=deg_to_rad(float(leg_data.get("lower_angle_deg", -45.0))),
                upper_angle_rad=deg_to_rad(float(leg_data.get("upper_angle_deg", 45.0))),
                dynamixel_id=int(leg_data.get("dynamixel_id", 0)),
            )
        )

    return ParallelIKParameters(
        ankle_center_base_mm=_tuple3(
            data["ankle_center_base_mm"], "ankle_center_base_mm"
        ),
        legs=tuple(legs),
    )
