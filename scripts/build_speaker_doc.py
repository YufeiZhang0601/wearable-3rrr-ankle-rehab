#!/usr/bin/env python3
"""Build a single-file speaker-notes ``.docx`` for Feishu / Lark import.

Produces ``slides/speaker_doc.docx`` containing the same content as the
PPT but laid out as one linearly-scrollable document: per slide we add
a section heading, an image (or a multi-image strip), the speaker-notes
script, and a separator. Designed to be uploaded to Feishu wiki via the
"\u5bfc\u5165" (import) button so that the user can present from a
scrolling document instead of from PowerPoint.

Run: ``python scripts/build_speaker_doc.py``
"""

import os
from copy import deepcopy

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "report", "figures")
OUT_PATH = os.path.join(ROOT, "slides", "speaker_doc.docx")

NAVY = RGBColor(0x0E, 0x2A, 0x47)
ACCENT = RGBColor(0xE6, 0x55, 0x1F)
GREY = RGBColor(0x55, 0x5C, 0x66)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def add_heading_para(doc, text, level, color=NAVY):
    p = doc.add_paragraph(style="Heading %d" % level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.color.rgb = color
    if level == 1:
        run.font.size = Pt(20)
    elif level == 2:
        run.font.size = Pt(16)
    else:
        run.font.size = Pt(13)
    run.bold = True
    return p


def add_para(doc, text, *, italic=False, color=None, size=11, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    return p


def add_bullets(doc, items, *, color=None, size=11):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        run = p.add_run(item)
        run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color


def add_image(doc, path, *, width_cm=14):
    if not os.path.exists(path):
        add_para(doc, "[missing image: %s]" % os.path.basename(path),
                 italic=True, color=ACCENT, size=10)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=Cm(width_cm))


def add_image_row(doc, paths, *, width_cm_each=7, captions=None):
    """Add a row of inline images (concatenated into a single paragraph)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for path in paths:
        if not os.path.exists(path):
            add_para(doc, "[missing image: %s]" % os.path.basename(path),
                     italic=True, color=ACCENT, size=10)
            continue
        run = p.add_run()
        run.add_picture(path, width=Cm(width_cm_each))
        run.add_text("  ")
    if captions:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cap.add_run("    \u2003".join(captions))
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = GREY


def add_speaker_block(doc, duration, lines):
    """Add a callout-style speaker-notes paragraph block."""
    add_para(doc, u"\U0001f3a4 Speaker notes  \u00b7  %s" % duration,
             bold=True, color=ACCENT, size=11)
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        run = p.add_run(line)
        run.font.size = Pt(11)


def add_code_block(doc, lines, *, title=None):
    """Add a monospaced "pseudocode" block."""
    if title:
        add_para(doc, title, bold=True, color=NAVY, size=11)
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(10)
        run.font.color.rgb = NAVY
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), "Consolas")


def add_separator(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "B0B0B0")
    pBdr.append(bottom)
    pPr.append(pBdr)


# ---------------------------------------------------------------------------
# main builder
# ---------------------------------------------------------------------------

def build():
    doc = Document()

    # title page ----------------------------------------------------------
    add_heading_para(
        doc,
        "Design and Validation of a Wearable Ankle Rehabilitation Robot "
        "with an Anatomically Aligned 3-RRR Spherical Parallel Mechanism",
        level=1,
    )
    add_para(doc, "AMR Research Course  \u00b7  Closing Presentation  \u00b7  May 2026",
             italic=True, color=GREY, size=12)
    add_para(doc, "Yufei Zhang  \u00b7  Department of Mechanical Engineering, "
             "Columbia University in the City of New York", size=11)
    add_para(doc, "Advisor: Prof. Sunil K. Agrawal  \u00b7  yz4917@columbia.edu",
             size=11, color=GREY)
    add_para(doc, "Code (MIT, open source): "
             "https://github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
             size=11, color=NAVY)
    add_image(doc, os.path.join(FIG, "cad_l1l2.png"), width_cm=11)
    add_separator(doc)

    # how-to-use note -----------------------------------------------------
    add_heading_para(doc, "How to use this document", level=2)
    add_para(doc,
             "This is a single scrolling speaker-notes document. Each "
             "section corresponds to one slide of the closing presentation. "
             "The visual at the top of each section is what the audience "
             "sees; the indented \u201cSpeaker notes\u201d block below is "
             "what you say. The full talk is paced for ~15 minutes.",
             size=11, color=GREY)
    add_separator(doc)

    # ---------- per-slide sections ----------
    section(doc, 1, "Title slide", "20\u202fs",
            images=[(os.path.join(FIG, "cad_l1l2.png"), 11)],
            notes=[
                "Good morning, everyone. Thank you for being here. My name "
                "is Yufei Zhang, and I am a graduate student in the "
                "Department of Mechanical Engineering, working with "
                "Professor Sunil K. Agrawal. Today I will walk you through "
                "my AMR research-course project: the design and validation "
                "of a wearable ankle rehabilitation robot with an "
                "anatomically aligned 3-RRR spherical parallel mechanism. "
                "The whole project \u2014 code, URDF, and this report "
                "\u2014 is open-source on GitHub at the link on the slide.",
            ])

    section(doc, 2, "Outline", "25\u202fs",
            bullets=[
                "1. Motivation: clinical need & gap in the state of the art",
                "2. Mechanism: anatomically aligned 3-RRR SPM + shoe-tray foot plate",
                "3. Kinematics: closed-form & numerical inverse kinematics",
                "4. Dynamics & baseline PID; proposed Assist-As-Needed control",
                "5. Embedded system & hardware integration",
                "6. Open-source ROS\u202f2 / Gazebo simulation pipeline",
                "7. Closed-loop tracking demo (recorded video)",
                "8. Planned ablation experiments & quantitative metrics",
                "9. Honest project status & invitation to extend",
            ],
            notes=[
                "Here is what I will cover in the next fifteen minutes. I "
                "will start with the clinical motivation and the gap in the "
                "state of the art, then introduce the mechanism \u2014 "
                "including the shoe-tray foot plate, which is one of our "
                "two structural innovations. After that, the kinematics, "
                "the baseline control, the proposed Assist-As-Needed law, "
                "and the embedded hardware. Then I will spend a few "
                "minutes on the open-source ROS\u202f2 / Gazebo simulation "
                "pipeline and the closed-loop tracking demo, before "
                "closing with the planned experiments, an honest project "
                "status, and an invitation for future students.",
            ])

    section(doc, 3, "Motivation: Clinical Need", "45\u202fs",
            images=[(os.path.join(FIG, "manual_therapy.png"), 14)],
            notes=[
                "Let me start with the clinical picture. Ankle injuries "
                "\u2014 sprains, fractures, post-operative cases \u2014 "
                "and neurological deficits like stroke and foot-drop are "
                "extremely common. The standard of care today is "
                "therapist-driven manual mobilization of the talocrural, "
                "subtalar, and tibiofibular joints. You can see a "
                "representative example on the slide. The problem is that "
                "manual therapy is highly dependent on clinician "
                "experience, the dosing is qualitative, and the trajectory "
                "is not measurable. A robotic device can give you "
                "repeatability, dose control, and objective outcome "
                "metrics \u2014 and that is exactly what motivates this work.",
            ])

    section(doc, 4, "State of the Art and the Gap", "60\u202fs",
            images=[
                (os.path.join(FIG, "lit_exoskeletons.png"), 14),
                (os.path.join(FIG, "lit_platforms.png"), 14),
            ],
            notes=[
                "If we look at the existing literature, ankle rehab "
                "devices fall into two big families. On the top, you have "
                "wearable exoskeletons \u2014 powered, passive, or "
                "quasi-passive. They are portable and easy to deploy, but "
                "they typically constrain the joint to one or at most two "
                "degrees of freedom. They mostly cover dorsiflexion and "
                "plantarflexion, and they ignore inversion and yaw \u2014 "
                "which are exactly the motions you need for proprioceptive "
                "ankle rehab.",
                "On the bottom, you have platform-style robots. They give "
                "you the full three to six degrees of freedom, but they "
                "are stationary, and their geometric center of rotation "
                "does not coincide with the patient's talocrural joint. "
                "That mismatch produces parasitic shear across the ankle, "
                "which is a safety concern.",
                "Our target is the gap between these two families: a "
                "wearable mechanism whose remote center of rotation is "
                "anatomically aligned with the human ankle.",
            ])

    section(doc, 5, "Biomechanical Motivation \u2192 3-RRR SPM", "50\u202fs",
            images=[(os.path.join(FIG, "ankle_anatomy_3rrr.png"), 16)],
            notes=[
                "The biomechanical reason this is even possible is shown "
                "on the left. The talocrural and subtalar complex has "
                "three rotation axes that converge near a single "
                "anatomical point. So if we use a mechanism whose joint "
                "axes also intersect at one common point \u2014 and "
                "place that point at the ankle \u2014 we get the same "
                "kinematic structure as the ankle itself. That is "
                "exactly what a 3-RRR spherical parallel mechanism does. "
                "On the right, you can see the canonical 3-RRR diagram: "
                "nine revolute joints arranged so all axes converge at "
                "the spherical center O, producing exactly three "
                "rotational degrees of freedom \u2014 pitch, roll, and "
                "yaw.",
            ])

    section(doc, 6, "Mechanism Design", "60\u202fs",
            image_row=(
                [(os.path.join(FIG, "cad_l1l2.png"), 8),
                 (os.path.join(FIG, "prototype_photo.png"), 5.5)],
                ["CAD with L\u2081 / L\u2082 annotation",
                 "3D-printed prototype"],
            ),
            notes=[
                "Here is the wearable embodiment we have built. It is a "
                "strap-mounted device with a contoured shank cuff at the "
                "top, three identical RRR limbs spaced at 120 degrees, "
                "and a foot plate at the bottom. Two things are worth "
                "highlighting on this slide. First, the link lengths "
                "L\u2081 on the proximal side and L\u2082 on the distal "
                "side are deliberately annotated, because \u2014 as you "
                "will see in two slides \u2014 their ratio directly "
                "governs the singularity placement and the rotational "
                "isotropy of the device. Second, on the right you can "
                "see the assembled 3D-printed prototype, which is what "
                "we use today to verify fit, clearance, and bench-level "
                "integration.",
            ])

    section(doc, 7,
            "Foot-Plate Innovation: Shoe-Tray Design", "75\u202fs",
            images=[(os.path.join(FIG, "cad_l1l2.png"), 11)],
            notes=[
                "Now I want to spend a slide on what I think is the more "
                "clinically interesting innovation, which is the foot-"
                "plate design. The classic options in the literature are "
                "either a rigid foot plate, which only fits one foot "
                "size, or a soft sandal, which loses stiffness. Neither "
                "generalizes well across patients.",
                "Our choice \u2014 informed by a survey of comparable "
                "rehab devices \u2014 is a shoe-tray foot plate. The "
                "subject keeps their own shoes and just steps into the "
                "tray. Velcro and straps fix the foot in place across "
                "the dorsum and around the heel, and the wearable "
                "strap-mounted device drives the tray as a rigid body.",
                "This buys us three concrete things. First, comfort: "
                "there is no direct skin contact, and the patient walks "
                "on their own shoe sole, so longer training sessions "
                "become tolerable. Second, generalization: a single "
                "device fits a wide range of foot sizes, roughly EU 36 "
                "through 46, without re-manufacturing. Third, clinical "
                "workflow: don and doff is a one-step \u201cstep-in\u201d "
                "motion, which matters in a real clinic.",
            ])

    section(doc, 8, "CAD Multi-View", "35\u202fs",
            image_row=(
                [(os.path.join(FIG, "cad_front.jpg"), 5.5),
                 (os.path.join(FIG, "cad_perspective.jpg"), 5.5),
                 (os.path.join(FIG, "cad_top.jpg"), 5.5)],
                ["(a) Front", "(b) Perspective", "(c) Top"],
            ),
            notes=[
                "Three views of the same CAD: front, perspective, and "
                "top. The two things I want you to notice are the "
                "symmetric three-limb topology around the shank cuff and "
                "the open-back base ring, which is what makes the device "
                "tolerant to different calf circumferences.",
            ])

    section(doc, 9, "Singularity-Aware Geometry", "60\u202fs",
            images=[(os.path.join(FIG, "workspace_plot.png"), 11)],
            notes=[
                "Now let me say a word about parallel singularities, "
                "because they are a real safety concern. At a parallel "
                "singularity the platform can pick up an extra, "
                "uncontrollable degree of freedom even when all the "
                "actuators are locked \u2014 meaning the device loses "
                "stiffness and can no longer resist external loads. In "
                "a rehab context that is dangerous.",
                "Following the analytical guidance of Saheb 2021 and Wu "
                "and Bai 2019 for the 3-RRR architecture, we picked the "
                "link ratio \u03c1 = L\u2082 / L\u2081 approximately "
                "equal to 1.15. The plot on the slide shows the per-leg "
                "reachable circles, and their intersection is the "
                "parallel-singularity-free common workspace. The result "
                "is roughly a 20\u202f% improvement in the global "
                "isotropy index of the rotational Jacobian, with the "
                "singular curves pushed outward toward the workspace "
                "boundary.",
            ])

    section(doc, 10, "Inverse Kinematics  (Algorithm 1)", "60\u202fs",
            code=("Algorithm 1  per-cycle parallel IK", [
                "input  : (roll, pitch, yaw), prior q\u207b",
                "output : motor angles q = (q1, q2, q3)",
                "",
                "R_BF \u2190 Rz(yaw) Ry(pitch) Rx(roll)",
                "for each leg i in {1, 2, 3}:",
                "    P_i  \u2190 R_BF \u00b7 P_i_F",
                "    f_i(q)  \u2190 |P_i \u2212 A_i(q)| \u2212 L_i",
                "    bracket  \u2190 grid containing q\u207b_i",
                "    q_i  \u2190 bisect(f_i, bracket)",
                "return q",
            ]),
            notes=[
                "The kinematics layer is what feeds the controller. We "
                "derived a closed-form inverse-kinematic expression per "
                "leg, which is great for offline workspace evaluation, "
                "and a numerical formulation for real-time control. The "
                "numerical version, summarized as Algorithm 1, takes the "
                "desired roll, pitch, and yaw, computes each platform-"
                "side point, and then for each leg it scans a coarse "
                "motor-angle grid for a sign change in the leg residual, "
                "runs bisection inside the bracket, and picks the root "
                "closest to the previous control cycle to enforce branch "
                "continuity. The whole thing runs in the Python standard "
                "library, with no external dependencies, which is what "
                "allows the same code to run inside a ROS\u202f2 node, "
                "inside a standalone CLI, and \u2014 eventually \u2014 "
                "inside the embedded loop on the Teensy.",
            ])

    section(doc, 11, "Dynamics & Baseline PID", "40\u202fs",
            image_row=(
                [(os.path.join(FIG, "underdamped_response.png"), 7.5),
                 (os.path.join(FIG, "critical_response.png"), 7.5)],
                ["Underdamped: Kp = 20, Kd = 0.5, Ki = 1",
                 "Critically damped: Kp = 50, Kd = 2, Ki = 5"],
            ),
            notes=[
                "For the baseline controller we use three independent "
                "PID loops on the actuator angles. The two plots show "
                "the platform orientation response to a step reference "
                "under two tunings. On the left, an underdamped tuning "
                "gives oscillatory settling \u2014 basically a soft, "
                "compliant interaction. On the right, a critically "
                "damped tuning gives fast, monotonic convergence. The "
                "point is that even on a rigid SPM, the feedback gains "
                "alone modulate effective compliance, and these two "
                "regimes bracket the spectrum that the AAN controller "
                "we are about to introduce will interpolate online.",
            ])

    section(doc, 12, "Assist-As-Needed Control  (proposed)", "60\u202fs",
            images=[(os.path.join(FIG, "aan_architecture.png"), 16)],
            notes=[
                "The AAN strategy comes from David Reinkensmeyer\u2019s "
                "group, and the idea is simple but powerful: the robot "
                "only assists when the patient actually needs help. If "
                "the patient can follow the trajectory on their own, the "
                "robot stays out of the way; if the patient starts "
                "drifting, the robot ramps up the assistance gradually. "
                "To estimate the patient torque without a distal force "
                "sensor, we subtract the model-predicted dynamic torque "
                "from the Dynamixel current measurement times the torque "
                "constant. The block on the slide shows the architecture: "
                "a high-level supervisor computes gait phase and "
                "asymmetry, schedules the assistance torque, and a low-"
                "level loop tracks it on the actuator. To be transparent: "
                "AAN is proposed and formulated, not yet deployed on "
                "real hardware.",
            ])

    section(doc, 13, "Embedded System & Hardware", "55\u202fs",
            image_row=(
                [(os.path.join(FIG, "electronics_breadboard.jpg"), 7.0),
                 (os.path.join(FIG, "hardware_wiring_diagram.jpg"), 7.0)],
                ["Prototype electronics stack",
                 "Servo control wiring (Dynamixel + U2D2 + PSU + host)"],
            ),
            notes=[
                "Two photos on this slide. On the left, the prototype "
                "electronics stack: a Teensy\u202f4.1 master in the "
                "center, an IMU breakout on the left for shank and foot "
                "orientation, and a TTL-to-RS-485 transceiver at the "
                "bottom that bridges the master to the daisy-chained "
                "Dynamixel actuator bus. On the right, the actual servo-"
                "control wiring used on the bench: the XM430 motor at "
                "the top, the ROBOTIS U2D2 communication board in the "
                "middle, the dedicated power supply on the right, and "
                "the host laptop at the bottom. Closed-loop control runs "
                "at 1\u202fkHz on the Teensy, with the encoder giving "
                "us roughly 0.088\u00b0 per tick \u2014 more than enough "
                "resolution for the angular precision required in ankle "
                "rehab.",
            ])

    section(doc, 14, "Open-Source ROS\u202f2 / Gazebo Pipeline",
            "60\u202fs",
            images=[(os.path.join(FIG, "gazebo_force_torque.png"), 16)],
            extra_paras=[
                ("Repository (MIT licensed):", True, NAVY, 11),
                ("https://github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
                 False, NAVY, 11),
            ],
            notes=[
                "One of the deliverables I am most proud of is the open-"
                "source simulation pipeline. The whole thing is shipped "
                "as a single ROS\u202f2 ament-python package, MIT "
                "licensed, at the URL above. It bundles the URDF and "
                "Xacro, twenty-two STL meshes, four launch files for "
                "visualization and Gazebo, and the parallel-IK solver as "
                "a shared kinematic core. The screenshot shows the "
                "workflow we use to gate URDF changes: we load the model "
                "into Gazebo, use the Apply Force and Torque dialog to "
                "inject a 100-newton-meter torque, and verify that the "
                "joint axes and inertials behave physically \u2014 no "
                "NaN inertias, no mesh interpenetration. This is what "
                "gives us confidence that any change to the robot "
                "description still simulates correctly before we touch "
                "hardware.",
            ])

    section(doc, 15, "Closed-Loop Tracking Demo  (Algorithm 2)",
            "45\u202fs",
            code=("Algorithm 2  closed-loop ankle-rehab tracking demo", [
                "parse URDF; pick (j1, j4, j6) as the three Dynamixel "
                "actuators",
                "q \u2190 0;   t \u2190 0",
                "while running:",
                "    sigma(t) \u2190 min(t / Tsoft, 1)         # soft start",
                "    pitch \u2190 sigma(t) * A_p * sin(2*pi*f*t)",
                "    roll  \u2190 sigma(t) * A_r * sin(2*pi*f*t)",
                "    q_ref \u2190 ParallelIK(roll, pitch, 0)   # Algo 1",
                "    dq    \u2190 clamp(q_ref - q,  qdot_max * dt)",
                "    tau   \u2190 clamp(controller(dq),  tau_max)",
                "    q     \u2190 q + dq                       # virtual actuator",
                "    log(t, q_ref, q, tau, ToTicks(q))           # CSV row",
                "    t \u2190 t + dt",
            ]),
            notes=[
                "Algorithm 2 shows the closed-loop tracking demo. It is "
                "dependency-free Python: it parses the URDF, treats "
                "joints 1, 4, and 6 as the three Dynamixel actuators, "
                "generates a slow sinusoidal reference at \u00b112\u00b0 "
                "of dorsi/plantarflexion and \u00b16\u00b0 of inversion, "
                "runs Algorithm 1 to get the motor angles, applies a "
                "1.2\u202fNm torque cap and a 0.8\u202frad/s velocity "
                "cap from the safety supervisor, and logs everything to "
                "CSV. A screen capture of the demo running against the "
                "URDF model is shipped in the repository as "
                "media/closed_loop_demo.mp4, about 25\u202fMB.",
            ])

    section(doc, 16, "Planned Experiments", "75\u202fs",
            two_columns=(
                ("Quantitative metrics", [
                    "Limb Symmetry Index (LSI) \u2013 north-star clinical metric",
                    "Jerk = d\u00b3x/dt\u00b3 from foot-plate IMU "
                    "(smoothness)",
                    "Interaction torque \u03c4_int (sensorless estimator)",
                    "Center of pressure (CoP) trajectory from gait mat",
                    "Human-contribution ratio  \u03b7_h = "
                    "\u03c4_ext / (\u03c4_ext + \u03c4_assist)",
                ]),
                ("Four sub-experiments", [
                    "E1  Simulated-impairment recovery (controlled foot-drop)",
                    "E2  Transparency evaluation (R\u00b2 \u2265 0.95 vs. barefoot)",
                    "E3  Active participation under AAN (\u03b7_h trend "
                    "across sessions)",
                    "E4  Passive transfer effect after a CPM bout",
                ]),
            ),
            notes=[
                "Now to the experimental design \u2014 which is fully "
                "designed but not yet executed.",
                "The metrics are drawn from the rehab-robotics "
                "literature: the Limb Symmetry Index as the north-star "
                "clinical metric, jerk as a smoothness indicator, the "
                "interaction torque from our sensorless estimator, the "
                "gait-mat center of pressure, and the human-"
                "contribution ratio.",
                "On the right, four sub-experiments. E1, simulated-"
                "impairment recovery, where we induce a controlled foot-"
                "drop with a small toe weight or a downward bias torque, "
                "and check whether AAN training brings the LSI from "
                "around 80\u202f% back toward 95\u202f%. E2, transparency "
                "\u2014 the device should not perturb natural gait under "
                "near-zero impedance, R squared above 0.95 between "
                "barefoot and device-on kinematics. E3, active "
                "participation, where the human-contribution ratio "
                "should rise across training sessions. And E4, the "
                "passive transfer effect of a CPM bout on overground "
                "gait. Statistics are within-subject paired tests with "
                "Bonferroni-Holm correction and bootstrap 95\u202f% "
                "confidence intervals.",
            ])

    section_status(doc)

    section(doc, 18, "Conclusion & Open Invitation", "60\u202fs",
            two_columns=(
                ("Delivered (turn-key)", [
                    "Wearable, anatomically-aligned 3-RRR SPM with the "
                    "shoe-tray foot plate that fits a wide range of "
                    "foot sizes",
                    "Closed-form + numerical IK that maps (roll, pitch, "
                    "yaw) to motor angles in real time",
                    "MIT-licensed ROS\u202f2 / Gazebo simulation "
                    "controller, verified end-to-end against the URDF",
                    "Ablation-experiment design and a full set of "
                    "quantitative rehab metrics (LSI, jerk, \u03c4_int, "
                    "CoP, \u03b7_h)",
                ]),
                ("Open for the next phase", [
                    "Standalone untethered operation: battery, free "
                    "wearable walking on the gait mat",
                    "Subject experiments E1\u2013E4: healthy-subject "
                    "simulated foot-drop \u2192 IRB-approved patient "
                    "cohort",
                ]),
            ),
            extra_paras=[
                ("\u2192  An open invitation to future students",
                 True, ACCENT, 12),
                ("The simulation codebase, the wearable hardware "
                 "design, and the experimental protocol together form a "
                 "turn-key starting point. Pull the repo, plug in your "
                 "own subject trials, and the project picks up exactly "
                 "where this report leaves off.",
                 False, GREY, 11),
            ],
            notes=[
                "So to summarize. The three concrete deliverables are: "
                "a wearable, anatomically aligned 3-RRR mechanism with "
                "a shoe-tray foot plate that fits a wide range of foot "
                "sizes; a closed-form plus numerical inverse-kinematic "
                "stack that runs in real time; and an MIT-licensed "
                "ROS\u202f2 / Gazebo simulation controller that has "
                "been verified end-to-end against the URDF.",
                "Two open items remain: standalone untethered "
                "operation, and the subject experiments E1 through E4.",
                "And here is the honest invitation. The simulation "
                "codebase, the wearable hardware design, and the "
                "experimental protocol together form a turn-key "
                "starting point. If a future student in our group is "
                "interested in this direction, they can pull the "
                "repository, plug in their own subject trials, and the "
                "project picks up exactly where this report leaves off. "
                "I would be very happy to support that.",
            ])

    section(doc, 19, "Thank You", "15\u202fs",
            extra_paras=[
                ("Thank you. \u00a0 Questions and discussion?",
                 True, NAVY, 16),
                ("Yufei Zhang  \u00b7  yz4917@columbia.edu",
                 False, GREY, 12),
                ("Advisor: Prof. Sunil K. Agrawal", False, GREY, 12),
                ("github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
                 False, NAVY, 12),
            ],
            notes=[
                "Thank you for your attention. I am happy to take "
                "questions.",
            ])

    if not os.path.isdir(os.path.dirname(OUT_PATH)):
        os.makedirs(os.path.dirname(OUT_PATH))
    out = OUT_PATH
    if os.path.exists(out):
        try:
            with open(out, "ab"):
                pass
        except PermissionError:
            base, ext = os.path.splitext(out)
            for i in range(2, 50):
                cand = "{}_v{}{}".format(base, i, ext)
                if not os.path.exists(cand):
                    out = cand
                    break
    doc.save(out)
    print("wrote " + out)


# ---------------------------------------------------------------------------
# section helpers
# ---------------------------------------------------------------------------

def section(doc, num, title, duration, *, images=None, image_row=None,
            bullets=None, code=None, two_columns=None, extra_paras=None,
            notes=None):
    add_heading_para(
        doc,
        u"Slide {n}\u2003\u00b7\u2003{t}".format(n=num, t=title),
        level=2,
    )
    if image_row is not None:
        paths_with_w, captions = image_row
        add_image_row(
            doc,
            [p for p, _ in paths_with_w],
            width_cm_each=paths_with_w[0][1],
            captions=captions,
        )
    if images:
        for p, w in images:
            add_image(doc, p, width_cm=w)
    if bullets:
        add_bullets(doc, bullets, size=11)
    if code is not None:
        title_text, code_lines = code
        add_code_block(doc, code_lines, title=title_text)
    if two_columns is not None:
        for col_title, col_items in two_columns:
            add_para(doc, col_title, bold=True, color=NAVY, size=12)
            add_bullets(doc, col_items, size=11)
    if extra_paras:
        for txt, bold, color, size in extra_paras:
            add_para(doc, txt, bold=bold, color=color, size=size)
    if notes:
        add_speaker_block(doc, duration, notes)
    add_separator(doc)


def section_status(doc):
    """Slide 17 \u2014 implementation status as a real Word table."""
    add_heading_para(
        doc,
        u"Slide 17\u2003\u00b7\u2003Implementation Status \u2014 "
        u"Honest Snapshot",
        level=2,
    )
    rows = [
        ("Wearable 3-RRR mechanism (\u03c1\u2248 1.15)",
         "Done", "+ ~20 % isotropy index"),
        ("Shoe-tray foot-plate design (size-generalizing, comfortable)",
         "Done", "Subject keeps own shoes"),
        ("Closed-form & numerical inverse kinematics",
         "Done", "Algorithm 1, in repo"),
        ("Open-source simulation controller (ROS\u202f2 + Gazebo)",
         "Done", "MIT-licensed release"),
        ("Closed-loop tracking demo against the URDF",
         "Done", "Algorithm 2 + recorded video"),
        ("Embedded electronics stack (Teensy + RS-485 + IMU)",
         "Done", "Bench-tested"),
        ("Ablation experiments + quantitative metrics designed",
         "Done", "LSI / jerk / \u03c4_int / CoP / \u03b7_h"),
        ("AAN control law formulated",
         "Proposed", "Eq. (16) - (18); pending HW deploy"),
        ("Standalone untethered operation (battery, free walking)",
         "Not yet", "Next milestone"),
        ("Human-subject experiments (E1\u2013E4)",
         "Not yet", "Platform built; subjects pending"),
    ]
    table = doc.add_table(rows=len(rows) + 1, cols=3)
    table.style = "Light Grid Accent 1"
    headers = ["Item", "Status", "Outcome / Notes"]
    for i, h in enumerate(headers):
        c = table.cell(0, i)
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(11)
    for r, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row):
            cell = table.cell(r, c_idx)
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            run.font.size = Pt(10)
            if c_idx == 1:
                run.bold = True
                run.font.color.rgb = (
                    NAVY if val == "Done"
                    else ACCENT if val == "Not yet"
                    else GREY
                )

    add_speaker_block(doc, "75\u202fs", [
        "I want to be very transparent with this slide, because honest "
        "framing matters. Here is what is done today, in dark navy. The "
        "wearable 3-RRR mechanism, the shoe-tray foot plate, the "
        "closed-form and numerical IK, the open-source simulation "
        "controller, the closed-loop tracking demo against the URDF, "
        "the bench-tested embedded electronics, and the full ablation-"
        "experiment design with quantitative metrics \u2014 these are "
        "all delivered, all in the repo, and all reproducible.",
        "Here is what is proposed but not yet hardware-deployed, in "
        "grey: the AAN control law itself. It is fully formulated, but "
        "it needs to ride on top of a real Dynamixel current loop "
        "before we can claim it works.",
        "And here is what is not yet done, in orange: first, "
        "standalone untethered operation \u2014 by which I mean "
        "battery-driven, free wearable walking on the gait mat. "
        "Second, the human-subject experiments themselves. The "
        "platform is built and runnable; the subject trials are "
        "simply the next milestone.",
    ])
    add_separator(doc)


if __name__ == "__main__":
    build()
