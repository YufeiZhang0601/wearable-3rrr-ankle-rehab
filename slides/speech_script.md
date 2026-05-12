# Closing Presentation — 15-Minute Speech Script

Deck: `slides/closing_presentation.pptx` (19 slides, 16:9)
Target length: **~14 min 30 s** plus ~30 s for the closing.
Pace: ~140 words / minute. Total script: **≈ 2,000 words**.

Notation: each slide block lists the slide number, its title, the rough
time you should spend on it, and the script (English; matches the
colloquial style of `Roar.docx` so you can deliver it from memory).

---

## Slide 1 — Title  *(~20 s)*

> Good morning, everyone. Thank you for being here. My name is Yufei
> Zhang, and I am a graduate student in the Department of Mechanical
> Engineering, working with Professor Sunil K. Agrawal. Today I will
> walk you through my AMR research-course project: the **design and
> validation of a wearable ankle rehabilitation robot with an
> anatomically aligned 3-RRR spherical parallel mechanism**. The whole
> project — code, URDF, and this report — is open-source on GitHub at
> the link you see on the slide.

## Slide 2 — Outline  *(~25 s)*

> Here is what I will cover in the next fifteen minutes. I will start
> with the clinical motivation and the gap in the state of the art,
> then introduce the mechanism — including the shoe-tray foot plate,
> which is one of our two structural innovations. After that, the
> kinematics, the baseline control, the proposed Assist-As-Needed law,
> and the embedded hardware. Then I will spend a few minutes on the
> open-source ROS 2 / Gazebo simulation pipeline and the closed-loop
> tracking demo, before closing with the planned experiments, an
> honest project status, and an invitation for future students.

---

## Slide 3 — Motivation: Clinical Need  *(~45 s)*

> Let me start with the clinical picture. Ankle injuries — sprains,
> fractures, post-operative cases — and neurological deficits like
> stroke and foot-drop are extremely common. The standard of care today
> is therapist-driven manual mobilization of the talocrural, subtalar,
> and tibiofibular joints. You can see a representative example on the
> slide. The problem is that manual therapy is highly dependent on
> clinician experience, the dosing is qualitative, and the trajectory
> is not measurable. A robotic device can give you repeatability, dose
> control, and objective outcome metrics — and that is exactly what
> motivates this work.

## Slide 4 — State of the Art and the Gap  *(~60 s)*

> If we look at the existing literature, ankle rehab devices fall into
> two big families. On the top, you have **wearable exoskeletons** —
> powered, passive, or quasi-passive. They are portable and easy to
> deploy, but they typically constrain the joint to one or at most two
> degrees of freedom. They mostly cover dorsiflexion and
> plantarflexion, and they ignore inversion and yaw — which are
> exactly the motions you need for proprioceptive ankle rehab.
>
> On the bottom, you have **platform-style robots**. They give you the
> full three to six degrees of freedom, but they are stationary, and
> their geometric center of rotation does not coincide with the
> patient's talocrural joint. That mismatch produces parasitic shear
> across the ankle, which is a safety concern.
>
> Our target is the gap between these two families: **a wearable
> mechanism whose remote center of rotation is anatomically aligned
> with the human ankle**.

## Slide 5 — Biomechanical Motivation → 3-RRR SPM  *(~50 s)*

> The biomechanical reason this is even possible is shown on the left.
> The talocrural and subtalar complex has three rotation axes that
> converge near a single anatomical point. So if we use a mechanism
> whose joint axes also intersect at one common point — and place that
> point at the ankle — we get the same kinematic structure as the
> ankle itself. That is exactly what a **3-RRR spherical parallel
> mechanism** does. On the right, you can see the canonical 3-RRR
> diagram: nine revolute joints arranged so all axes converge at the
> spherical center O, producing exactly three rotational degrees of
> freedom — pitch, roll, and yaw.

---

## Slide 6 — Mechanism Design  *(~60 s)*

> Here is the wearable embodiment we have built. It is a strap-mounted
> device with a contoured shank cuff at the top, three identical RRR
> limbs spaced at 120 degrees, and a foot plate at the bottom. Two
> things are worth highlighting on this slide. First, the link lengths
> L₁ on the proximal side and L₂ on the distal side are deliberately
> annotated, because — as you will see in two slides — their ratio
> directly governs the singularity placement and the rotational
> isotropy of the device. Second, on the right you can see the
> assembled 3D-printed prototype, which is what we use today to verify
> fit, clearance, and bench-level integration.

## Slide 7 — Foot-Plate Innovation: Shoe-Tray Design  *(~75 s)*

> Now I want to spend a slide on what I think is the more clinically
> interesting innovation, which is the foot-plate design. The classic
> options in the literature are either a rigid foot plate, which only
> fits one foot size, or a soft sandal, which loses stiffness. Neither
> generalizes well across patients.
>
> Our choice — informed by a survey of comparable rehab devices — is
> a **shoe-tray foot plate**. The subject keeps their own shoes and
> just steps into the tray. Velcro and straps fix the foot in place
> across the dorsum and around the heel, and the wearable
> strap-mounted device drives the tray as a rigid body.
>
> This buys us three concrete things. First, **comfort**: there is no
> direct skin contact, and the patient walks on their own shoe sole,
> so longer training sessions become tolerable. Second,
> **generalization**: a single device fits a wide range of foot sizes,
> roughly EU 36 through 46, without re-manufacturing. Third,
> **clinical workflow**: don and doff is a one-step "step-in" motion,
> which matters in a real clinic.

## Slide 8 — CAD Multi-View  *(~35 s)*

> Three views of the same CAD: front, perspective, and top. The two
> things I want you to notice are the symmetric three-limb topology
> around the shank cuff and the open-back base ring, which is what
> makes the device tolerant to different calf circumferences.

## Slide 9 — Singularity-Aware Geometry  *(~60 s)*

> Now let me say a word about parallel singularities, because they
> are a real safety concern. At a parallel singularity the platform
> can pick up an extra, uncontrollable degree of freedom even when all
> the actuators are locked — meaning the device loses stiffness and
> can no longer resist external loads. In a rehab context that is
> dangerous.
>
> Following the analytical guidance of Saheb 2021 and Wu and Bai 2019
> for the 3-RRR architecture, we picked the link ratio ρ = L₂ / L₁
> approximately equal to 1.15. The plot on the left shows the per-leg
> reachable circles, and their intersection is the parallel-singularity
> -free common workspace. The result is a **roughly 20 % improvement
> in the global isotropy index** of the rotational Jacobian, with the
> singular curves pushed outward toward the workspace boundary.

## Slide 10 — Inverse Kinematics  *(~60 s)*

> The kinematics layer is what feeds the controller. We derived a
> closed-form inverse-kinematic expression per leg, which is great
> for offline workspace evaluation, and a numerical formulation for
> real-time control. The numerical version, summarized as Algorithm 1
> on the right, takes the desired roll, pitch, and yaw, computes each
> platform-side point, and then for each leg it scans a coarse motor-
> angle grid for a sign change in the leg residual, runs bisection
> inside the bracket, and picks the root closest to the previous
> control cycle to enforce branch continuity. The whole thing runs in
> the Python standard library, with no external dependencies, which is
> what allows the same code to run inside a ROS 2 node, inside a
> standalone CLI, and — eventually — inside the embedded loop on the
> Teensy.

## Slide 11 — Dynamics & Baseline PID  *(~40 s)*

> For the baseline controller we use three independent PID loops on
> the actuator angles. The two plots show the platform orientation
> response to a step reference under two tunings. On the left, an
> underdamped tuning gives oscillatory settling — basically a soft,
> compliant interaction. On the right, a critically damped tuning
> gives fast, monotonic convergence. The point is that even on a
> rigid SPM, the feedback gains alone modulate effective compliance,
> and these two regimes bracket the spectrum that the AAN controller
> we are about to introduce will interpolate online.

## Slide 12 — Assist-As-Needed Control  *(~60 s)*

> The AAN strategy comes from David Reinkensmeyer's group, and the
> idea is simple but powerful: the robot only assists when the patient
> actually needs help. If the patient can follow the trajectory on
> their own, the robot stays out of the way; if the patient starts
> drifting, the robot ramps up the assistance gradually. To estimate
> the patient torque without a distal force sensor, we subtract the
> model-predicted dynamic torque from the Dynamixel current
> measurement times the torque constant. The block on the right shows
> the architecture: a high-level supervisor computes gait phase and
> asymmetry, schedules the assistance torque, and a low-level loop
> tracks it on the actuator. To be transparent: AAN is **proposed and
> formulated**, not yet deployed on real hardware.

---

## Slide 13 — Embedded System & Hardware  *(~55 s)*

> Two photos on this slide. On the left, the prototype electronics
> stack: a Teensy 4.1 master in the center, an IMU breakout on the
> left for shank and foot orientation, and a TTL-to-RS-485
> transceiver at the bottom that bridges the master to the daisy-
> chained Dynamixel actuator bus. On the right, the actual servo-
> control wiring used on the bench: the XM430 motor at the top, the
> ROBOTIS U2D2 communication board in the middle, the dedicated power
> supply on the right, and the host laptop at the bottom. Closed-loop
> control runs at 1 kHz on the Teensy, with the encoder giving us
> roughly 0.088 degrees per tick — more than enough resolution for
> the angular precision required in ankle rehab.

## Slide 14 — Open-Source ROS 2 / Gazebo Pipeline  *(~60 s)*

> One of the deliverables I am most proud of is the open-source
> simulation pipeline. The whole thing is shipped as a single ROS 2
> ament-python package, MIT licensed, at the URL on the right. It
> bundles the URDF and Xacro, twenty-two STL meshes, four launch
> files for visualization and Gazebo, and the parallel-IK solver as a
> shared kinematic core. The screenshot on the left shows the
> workflow we use to gate URDF changes: we load the model into Gazebo,
> use the Apply Force and Torque dialog to inject a 100-newton-meter
> torque, and verify that the joint axes and inertials behave
> physically — no NaN inertias, no mesh interpenetration. This is
> what gives us confidence that any change to the robot description
> still simulates correctly before we touch hardware.

## Slide 15 — Closed-Loop Tracking Demo  *(~45 s)*

> Algorithm 2 shows the closed-loop tracking demo. It is dependency-
> free Python: it parses the URDF, treats joints 1, 4, and 6 as the
> three Dynamixel actuators, generates a slow sinusoidal reference at
> ±12 degrees of dorsi/plantarflexion and ±6 degrees of inversion, runs
> Algorithm 1 to get the motor angles, applies a 1.2 newton-meter
> torque cap and a 0.8 radian-per-second velocity cap from the safety
> supervisor, and logs everything to CSV. A screen capture of the demo
> running against the URDF model is shipped in the repository as
> `media/closed_loop_demo.mp4`, about 25 megabytes.

---

## Slide 16 — Planned Experiments  *(~75 s)*

> Now to the experimental design — which is **fully designed but not
> yet executed**.
>
> The metrics, on the left, are drawn from the rehab-robotics
> literature: the **Limb Symmetry Index** as the north-star clinical
> metric, **jerk** as a smoothness indicator, the **interaction torque**
> from our sensorless estimator, the gait-mat **center of pressure**,
> and the **human-contribution ratio** — what fraction of total
> joint torque comes from the patient under AAN.
>
> On the right, four sub-experiments. **E1**, simulated-impairment
> recovery, where we induce a controlled foot-drop with a small toe
> weight or a downward bias torque, and check whether AAN training
> brings the LSI from around 80 % back toward 95 %. **E2**, transparency
> — the device should not perturb natural gait under near-zero
> impedance, R squared above 0.95 between barefoot and device-on
> kinematics. **E3**, active participation, where the human-contribution
> ratio should rise across training sessions. And **E4**, the passive
> transfer effect of a CPM bout on overground gait. Statistics are
> within-subject paired tests with Bonferroni-Holm correction and
> bootstrap 95 % confidence intervals.

## Slide 17 — Implementation Status — Honest Snapshot  *(~75 s)*

> I want to be very transparent with this slide, because honest
> framing matters. Here is what is **done** today, in dark navy. The
> wearable 3-RRR mechanism, the shoe-tray foot plate, the closed-form
> and numerical IK, the open-source simulation controller, the
> closed-loop tracking demo against the URDF, the bench-tested
> embedded electronics, and the full ablation-experiment design with
> quantitative metrics — these are all delivered, all in the repo,
> and all reproducible.
>
> Here is what is **proposed but not yet hardware-deployed**, in
> grey: the AAN control law itself. It is fully formulated, but it
> needs to ride on top of a real Dynamixel current loop before we
> can claim it works.
>
> And here is what is **not yet done**, in orange: first, standalone
> untethered operation — by which I mean battery-driven, free
> wearable walking on the gait mat. Second, the human-subject
> experiments themselves. The platform is built and runnable; the
> subject trials are simply the next milestone.

## Slide 18 — Conclusion & Open Invitation  *(~60 s)*

> So to summarize. The three concrete deliverables are: a wearable,
> anatomically aligned 3-RRR mechanism with a shoe-tray foot plate
> that fits a wide range of foot sizes; a closed-form plus numerical
> inverse-kinematic stack that runs in real time; and an MIT-licensed
> ROS 2 / Gazebo simulation controller that has been verified end-to-
> end against the URDF.
>
> Two open items remain: standalone untethered operation, and the
> subject experiments E1 through E4.
>
> And here is the honest invitation. The simulation codebase, the
> wearable hardware design, and the experimental protocol together
> form a turn-key starting point. If a future student in our group is
> interested in this direction, they can pull the repository, plug in
> their own subject trials, and the project picks up exactly where
> this report leaves off. I would be very happy to support that.

## Slide 19 — Thank You  *(~15 s)*

> Thank you for your attention. I am happy to take questions.

---

## Time budget

| Block | Slides | Target |
|---|---|---|
| Opening | 1 – 2 | 0:45 |
| Motivation & gap | 3 – 4 | 1:45 |
| Mechanism + shoe-tray | 5 – 8 | 3:40 |
| Kinematics + control | 9 – 12 | 3:20 |
| Hardware + open-source | 13 – 15 | 2:40 |
| Experiments + status | 16 – 17 | 2:30 |
| Closing | 18 – 19 | 1:15 |
| **Total** | **19 slides** | **~15:55** |

If you find yourself running long on the day, the easiest cuts are:
slide 8 (CAD multi-view, optional), slide 11 (PID tunings, can be one
sentence), slide 15 (closed-loop demo, can be skipped if you screen
the video instead). Cutting all three saves ~2 minutes and brings the
talk to ~13:30.
