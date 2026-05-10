# RH1 STEP Kinematics Extraction

This workflow turns the SolidWorks STEP assembly into a short list of geometry
candidates that can be confirmed and copied into an IK parameter file.

## Generate candidates

From the repository root:

```bash
python3 scripts/extract_step_kinematics.py assem_v3.STEP
```

On Windows PowerShell:

```powershell
python scripts\extract_step_kinematics.py assem_v3.STEP
```

The script writes:

```text
demo_output/step_kinematics_candidates.json
demo_output/step_kinematics_candidates.md
```

For the current `assem_v3.STEP`, the strongest unverified actuator-axis
candidates have also been copied into:

```text
params/kinematic_params.candidate.yaml
```

Treat that file as a starting point, not as a validated IK model.

## What to confirm

The STEP file contains many circular holes and shafts, so the script reports
candidates instead of pretending to know the mechanism. Confirm these values in
SolidWorks or by visual inspection:

- `joint1`, `joint4`, `joint6`: the three XM430 output axes.
- `p1`, `p2`, `p3`: the three moving-platform connection axes/points on the
  foot plate.
- `ankle_center_base_mm`: the intended spherical center of rotation.
- `zero_angle_rad`: the motor angle offset when the CAD assembly is in the
  neutral foot-plate pose.

## Parameter file shape

Copy confirmed candidates into a file such as
`params/kinematic_params.yaml`:

```yaml
units: millimeter
source_step: assem_v3.STEP

ankle_center_base_mm: [0.0, 0.0, 0.0]

actuators:
  joint1:
    axis_point_base_mm: [0.0, 0.0, 0.0]
    axis_direction_base: [0.0, 0.0, 1.0]
    zero_angle_rad: 0.0
    dynamixel_id: 1
  joint4:
    axis_point_base_mm: [0.0, 0.0, 0.0]
    axis_direction_base: [0.0, 0.0, 1.0]
    zero_angle_rad: 0.0
    dynamixel_id: 2
  joint6:
    axis_point_base_mm: [0.0, 0.0, 0.0]
    axis_direction_base: [0.0, 0.0, 1.0]
    zero_angle_rad: 0.0
    dynamixel_id: 3

foot_plate:
  neutral_frame_base:
    origin_mm: [0.0, 0.0, 0.0]
    x_axis: [1.0, 0.0, 0.0]
    y_axis: [0.0, 1.0, 0.0]
    z_axis: [0.0, 0.0, 1.0]
  connection_points_foot_mm:
    p1: [0.0, 0.0, 0.0]
    p2: [0.0, 0.0, 0.0]
    p3: [0.0, 0.0, 0.0]
```

## Why this is still a candidate workflow

The current STEP export is AP203. It preserves solid geometry and part names,
but it does not reliably expose SolidWorks mate semantics. A dependency-free
parser can find cylinder axes, but it cannot always know which cylinder is a
motor output shaft versus a screw hole.

If possible, re-export as STEP AP242 with named reference geometry:

```text
motor_axis_1, motor_axis_2, motor_axis_3
p1, p2, p3
ankle_center
base_frame
foot_frame
```

That makes the final IK parameter extraction much less ambiguous.
