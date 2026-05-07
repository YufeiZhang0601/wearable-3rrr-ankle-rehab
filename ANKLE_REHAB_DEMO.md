# RH1 Ankle Rehab Closed-Loop Demo

This repository currently contains a ROS 2 robot description package exported
from SolidWorks. The runnable demo is:

```powershell
python scripts\ankle_rehab_closed_loop_demo.py
```

The script parses `urdf/rh1.urdf`, uses `joint1`, `joint4`, and `joint6` as the
three virtual XM430-W350-R actuators, tracks a slow ankle rehabilitation
trajectory, and writes feedback data to:

```text
demo_output/ankle_rehab_closed_loop.csv
```

## Control Demo

The default motion is intentionally conservative for early ankle rehab testing:

- dorsiflexion/plantarflexion amplitude: `12 deg`
- inversion/eversion amplitude: `6 deg`
- cycle frequency: `0.05 Hz`
- smooth startup ramp: `3 s`
- torque limit used in simulation: `1.2 Nm`
- velocity limit used in simulation: `0.8 rad/s`

The XM430-W350-R stall torque is treated as an upper hard cap, but this demo
uses a lower patient-side torque limit by default. Tune this only after the
mechanism is unloaded, then tested with a fixture, and only then with a human
subject under lab safety procedures.

Useful command examples:

```powershell
python scripts\ankle_rehab_closed_loop_demo.py --duration 60
python scripts\ankle_rehab_closed_loop_demo.py --dorsi-amp-deg 8 --invert-amp-deg 4
python scripts\ankle_rehab_closed_loop_demo.py --torque-limit-nm 0.8 --velocity-limit-rad-s 0.5
```

## URDF Assumptions

The current URDF tree defines the main revolute joints, while the Gazebo block at
the end adds two extra closed-chain joints. Generic URDF parsers do not enforce
those Gazebo-only loop constraints, so this first demo runs a stable actuator
feedback loop rather than a full closed-chain physics solve.

Important current URDF issues before Gazebo or hardware control:

- all revolute joint limits have `effort="0"` and `velocity="0"`;
- mesh files referenced by `package://rh1/meshes/visual/*.STL` are not present in
  this workspace snapshot;
- the Gazebo-only closed-chain joints should be modeled explicitly in SDF/Gazebo
  or replaced with a physics-engine-supported constraint model.

## Hardware Mapping

The demo exports Dynamixel position goal ticks centered around `2048`, using the
XM430 position resolution of about `0.087912 deg/tick`. It does not send commands
to motors.

A safe hardware bring-up path is:

1. Run this script and inspect the CSV tracking and goal ticks.
2. Add a Dynamixel SDK bridge that sends the three goal ticks to the motor IDs
   mapped to `joint1`, `joint4`, and `joint6`.
3. Read motor position/current feedback and replace the simulated measured
   states with real measurements.
4. Add Vive tracker ankle pose as the outer-loop feedback signal.
5. Add gait mat contact/stance events to gate motion, pause during unsafe
   loading, or switch between passive ROM and assist-as-needed modes.
