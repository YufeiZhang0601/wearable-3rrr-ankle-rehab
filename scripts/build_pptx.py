#!/usr/bin/env python3
"""Build the AMR-research closing-presentation PPTX from the report assets.

Produces ``slides/closing_presentation.pptx`` using ``python-pptx``. All figures
are sourced from ``report/figures/`` and one new wiring photo. The deck mirrors
the section ordering of ``report/main.tex`` and is intended for in-person
defense / closing presentation in roughly 15--20 minutes.

Run: ``python scripts/build_pptx.py``
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.4)
HEADER_H = Inches(0.75)

NAVY = RGBColor(0x0E, 0x2A, 0x47)
ACCENT = RGBColor(0xE6, 0x55, 0x1F)
GREY = RGBColor(0x55, 0x5C, 0x66)
LIGHT_GREY = RGBColor(0xF1, 0xF3, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

TITLE_FONT = "Calibri"
BODY_FONT = "Calibri"
MONO_FONT = "Consolas"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(REPO_ROOT, "report", "figures")
OUT_DIR = os.path.join(REPO_ROOT, "slides")
OUT_PATH = os.path.join(OUT_DIR, "closing_presentation.pptx")


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def add_blank(prs):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H
    )
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    return slide


def add_text(slide, x, y, w, h, text, *, size=18, bold=False, color=None,
             font=BODY_FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color if color is not None else NAVY
    return box


def add_bullets(slide, x, y, w, h, items, *, size=16, color=None):
    color = color or RGBColor(0x22, 0x22, 0x22)
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = u"\u2022  " + item
        run.font.name = BODY_FONT
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return box


def add_header(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, HEADER_H
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    add_text(slide, MARGIN, Inches(0.12), SLIDE_W - 2 * MARGIN, Inches(0.55),
             title, size=24, bold=True, color=WHITE,
             font=TITLE_FONT, anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, MARGIN, HEADER_H + Inches(0.05),
            Inches(0.12), Inches(0.32)
        )
        accent.line.fill.background()
        accent.fill.solid()
        accent.fill.fore_color.rgb = ACCENT
        add_text(slide, MARGIN + Inches(0.22), HEADER_H + Inches(0.04),
                 SLIDE_W - 2 * MARGIN, Inches(0.34),
                 subtitle, size=14, bold=False, color=GREY,
                 anchor=MSO_ANCHOR.MIDDLE)


def add_footer(slide, page_num, total):
    add_text(slide, MARGIN, SLIDE_H - Inches(0.32),
             Inches(8), Inches(0.25),
             "Yufei Zhang  \u00b7  AMR Research Course  \u00b7  May 2026",
             size=10, color=GREY)
    add_text(slide, SLIDE_W - Inches(1.1), SLIDE_H - Inches(0.32),
             Inches(0.7), Inches(0.25),
             "{} / {}".format(page_num, total),
             size=10, color=GREY, align=PP_ALIGN.RIGHT)


def add_image(slide, path, x, y, w=None, h=None):
    if not os.path.exists(path):
        add_text(slide, x, y, w or Inches(2), h or Inches(0.5),
                 "[missing image: {}]".format(os.path.basename(path)),
                 size=12, color=ACCENT)
        return None
    return slide.shapes.add_picture(path, x, y, width=w, height=h)


def add_caption(slide, x, y, w, text):
    add_text(slide, x, y, w, Inches(0.32), text,
             size=11, color=GREY, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# slide builders
# ---------------------------------------------------------------------------

def slide_title(prs):
    s = add_blank(prs)
    block = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(2.6))
    block.line.fill.background()
    block.fill.solid()
    block.fill.fore_color.rgb = NAVY
    add_text(s, MARGIN, Inches(0.55),
             SLIDE_W - 2 * MARGIN, Inches(0.4),
             "AMR Research Course  \u00b7  Closing Presentation",
             size=14, color=ACCENT, bold=True, font=TITLE_FONT)
    add_text(s, MARGIN, Inches(0.95),
             SLIDE_W - 2 * MARGIN, Inches(1.6),
             "Design and Validation of a Wearable Ankle "
             "Rehabilitation Robot with an Anatomically Aligned "
             "3-RRR Spherical Parallel Mechanism",
             size=30, bold=True, color=WHITE, font=TITLE_FONT)

    add_text(s, MARGIN, Inches(3.0),
             SLIDE_W - 2 * MARGIN, Inches(0.5),
             "Yufei Zhang", size=22, bold=True)
    add_text(s, MARGIN, Inches(3.55),
             SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Department of Mechanical Engineering, "
             "Columbia University in the City of New York",
             size=14, color=GREY)
    add_text(s, MARGIN, Inches(3.95),
             SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Advisor:  Prof. Sunil K. Agrawal", size=14, color=GREY)
    add_text(s, MARGIN, Inches(4.3),
             SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Email:  yz4917@columbia.edu", size=14, color=GREY)

    add_text(s, MARGIN, Inches(5.7),
             SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Source code (MIT, open-source):", size=12, color=GREY)
    add_text(s, MARGIN, Inches(6.05),
             SLIDE_W - 2 * MARGIN, Inches(0.5),
             "github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
             size=18, bold=True, color=NAVY, font=MONO_FONT)

    add_image(s, os.path.join(FIG, "cad_l1l2.png"),
              SLIDE_W - Inches(3.6), Inches(2.9),
              w=Inches(3.2))


def slide_outline(prs):
    s = add_blank(prs)
    add_header(s, "Outline", "How the next 18 minutes are structured")
    items = [
        "1.  Motivation: clinical need & gap in the state of the art",
        "2.  Mechanism: anatomically aligned 3-RRR SPM, wearable form factor",
        "3.  Kinematics: closed-form & numerical inverse kinematics",
        "4.  Dynamics & baseline PID; proposed Assist-As-Needed control",
        "5.  Embedded system & hardware integration",
        "6.  Open-source ROS\u202f2 / Gazebo design-and-validation pipeline",
        "7.  Closed-loop tracking demo (recorded video)",
        "8.  Planned experiments & implementation status",
        "9.  Conclusion & future work",
    ]
    add_bullets(s, MARGIN, Inches(1.4), SLIDE_W - 2 * MARGIN, Inches(5.3),
                items, size=20)


def slide_motivation(prs):
    s = add_blank(prs)
    add_header(s, "Motivation: Clinical Need",
               "Why a robotic, dose-controlled ankle rehab device?")
    add_bullets(s, MARGIN, Inches(1.4), Inches(6.2), Inches(5.0), [
        "Ankle injuries (sprains, fractures, post-op) and neurological "
        "deficits (stroke, foot-drop) are very common",
        "Standard of care is therapist-driven manual mobilization "
        "(talocrural, subtalar, tibiofibular joints)",
        "Highly dependent on clinician experience; little quantitative "
        "dosing or trajectory tracking",
        "Robotic platforms can provide repeatability, dose control, and "
        "objective outcome metrics  \u2192  this work",
    ], size=18)
    add_image(s, os.path.join(FIG, "manual_therapy.png"),
              Inches(7.0), Inches(1.5), w=Inches(5.9))
    add_caption(s, Inches(7.0), Inches(6.6), Inches(5.9),
                "Clinical reference: manual ankle mobilization")


def slide_state_of_art(prs):
    s = add_blank(prs)
    add_header(s, "State of the Art & the Gap",
               "Wearable exoskeletons vs. platform-style ankle rehab robots")
    add_image(s, os.path.join(FIG, "lit_exoskeletons.png"),
              MARGIN, Inches(1.3), w=Inches(6.2))
    add_caption(s, MARGIN, Inches(4.0), Inches(6.2),
                "(a) Wearable exoskeletons \u2013 portable, often 1\u20132 DOF")
    add_image(s, os.path.join(FIG, "lit_platforms.png"),
              MARGIN, Inches(4.4), w=Inches(6.2))
    add_caption(s, MARGIN, Inches(7.05), Inches(6.2),
                "(b) Platform robots \u2013 multi-DOF, but stationary & non-anthropomorphic")
    add_bullets(s, Inches(7.0), Inches(1.4),
                SLIDE_W - Inches(7.0) - MARGIN, Inches(5.0), [
        "Existing wearable devices: only 1\u20132 DOF, miss inversion / "
        "yaw motion of the ankle complex",
        "Existing platform robots: full 3\u20136 DOF, but stationary, and "
        "their center of rotation does NOT coincide with the talocrural "
        "joint  \u2192  parasitic shear",
        "This work: target the gap \u2014 a wearable mechanism whose "
        "remote center of rotation is anatomically aligned with the "
        "human ankle",
    ], size=16)


def slide_anatomy(prs):
    s = add_blank(prs)
    add_header(s, "Biomechanical Motivation \u2192 3-RRR SPM",
               "Anatomy of the talocrural / subtalar complex matches a "
               "spherical mechanism")
    add_image(s, os.path.join(FIG, "ankle_anatomy_3rrr.png"),
              MARGIN, Inches(1.4), w=Inches(8.5))
    add_bullets(s, Inches(9.2), Inches(1.4),
                SLIDE_W - Inches(9.2) - MARGIN, Inches(5.5), [
        "Ankle: 3 rotation axes converge near a single anatomical point",
        "3-RRR SPM: 9 revolute joints whose axes intersect at one "
        "common spherical center O",
        "Three pure rotations \u2261 dorsi/plantarflexion, "
        "inversion/eversion, internal/external rotation",
        "Aligning O with the talocrural complex eliminates parasitic "
        "translation",
    ], size=15)


def slide_mechanism(prs):
    s = add_blank(prs)
    add_header(s, "Mechanism Design",
               "Wearable embodiment with annotated link lengths "
               "L\u2081 (proximal) and L\u2082 (distal)")
    add_image(s, os.path.join(FIG, "cad_l1l2.png"),
              MARGIN, Inches(1.3), w=Inches(5.6))
    add_caption(s, MARGIN, Inches(6.6), Inches(5.6),
                "CAD render with link annotation L\u2081 / L\u2082")
    add_image(s, os.path.join(FIG, "prototype_photo.png"),
              Inches(6.6), Inches(1.3), w=Inches(3.6))
    add_caption(s, Inches(6.6), Inches(6.6), Inches(3.6),
                "3D-printed prototype (assembled)")
    add_bullets(s, Inches(10.5), Inches(1.4),
                SLIDE_W - Inches(10.5) - MARGIN, Inches(5.5), [
        "Three identical RRR limbs at 120\u00b0",
        "Open-back base ring + adjustable shank cuff",
        "Foot plate as moving end-effector",
        "3D-printed for design iteration",
        "All actuator axes intersect at the ankle center",
    ], size=14)


def slide_cad_views(prs):
    s = add_blank(prs)
    add_header(s, "CAD Multi-View",
               "Three views of the wearable form factor")
    w = Inches(4.0)
    y = Inches(1.6)
    add_image(s, os.path.join(FIG, "cad_front.jpg"),
              MARGIN, y, w=w)
    add_caption(s, MARGIN, y + Inches(4.4), w, "(a) Front")
    add_image(s, os.path.join(FIG, "cad_perspective.jpg"),
              MARGIN + w + Inches(0.3), y, w=w)
    add_caption(s, MARGIN + w + Inches(0.3), y + Inches(4.4), w,
                "(b) Perspective")
    add_image(s, os.path.join(FIG, "cad_top.jpg"),
              MARGIN + 2 * (w + Inches(0.3)), y, w=w)
    add_caption(s, MARGIN + 2 * (w + Inches(0.3)), y + Inches(4.4), w,
                "(c) Top")


def slide_singularity(prs):
    s = add_blank(prs)
    add_header(s, "Singularity-Aware Geometry",
               "Link ratio \u03c1 = L\u2082 / L\u2081 controls the "
               "rotational-Jacobian conditioning")
    add_image(s, os.path.join(FIG, "workspace_plot.png"),
              MARGIN, Inches(1.5), w=Inches(6.4))
    add_caption(s, MARGIN, Inches(6.4), Inches(6.4),
                "Per-leg reachable circles \u2192 their intersection is the "
                "singularity-free common workspace")
    add_bullets(s, Inches(7.2), Inches(1.5),
                SLIDE_W - Inches(7.2) - MARGIN, Inches(5.0), [
        "Type-2 singularity: det(A) \u2192 0 \u2192 platform loses "
        "stiffness \u2192 unsafe under patient load",
        "Following Saheb \u2026 (2021) and Wu & Bai (2019), pick "
        "\u03c1 \u2248 1.15",
        "Result: + ~20 % global isotropy index of J\u1d63",
        "Result: singular curves pushed to the workspace boundary",
        "\u2192 stiffness preserved across the clinical ROM",
    ], size=16)


def slide_kinematics(prs):
    s = add_blank(prs)
    add_header(s, "Inverse Kinematics  (Algorithm 1)",
               "Closed-form derivation \u2192 numerical bisection for "
               "real-time control")
    add_text(s, MARGIN, Inches(1.4), Inches(6.2), Inches(0.4),
             "Closed-form (per leg):", size=16, bold=True)
    add_bullets(s, MARGIN, Inches(1.85), Inches(6.2), Inches(2.6), [
        "B\u1d62 = A\u1d62 + \u03b7 (C\u1d62 \u2212 A\u1d62) + "
        "\u03be \u2027 ((C\u1d62 \u2212 A\u1d62) \u00d7 N) / |\u00b7|",
        "\u03b8\u1d62 = arccos( (B\u1d62 \u2212 A\u1d62) \u00b7 u\u1d62 / "
        "|B\u1d62 \u2212 A\u1d62| )",
        "Used for offline workspace evaluation",
    ], size=15)
    add_text(s, MARGIN, Inches(4.7), Inches(6.2), Inches(0.4),
             "Numerical (real-time, used in code):",
             size=16, bold=True)
    add_bullets(s, MARGIN, Inches(5.15), Inches(6.2), Inches(2.0), [
        "Each leg: scalar residual f\u1d62(q\u1d62) = "
        "|P\u1d62 \u2212 A\u1d62(q\u1d62)| \u2212 L\u1d62",
        "Coarse bracket \u2192 bisection \u2192 root-continuity rule",
        "Dependency-free, runs in ROS\u202f2 and on host laptop alike",
    ], size=15)

    box_x = Inches(7.0)
    box_y = Inches(1.4)
    box_w = SLIDE_W - box_x - MARGIN
    box_h = Inches(5.6)
    bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, box_x, box_y,
                            box_w, box_h)
    bg.line.color.rgb = NAVY
    bg.line.width = Pt(1)
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT_GREY
    add_text(s, box_x + Inches(0.2), box_y + Inches(0.1),
             box_w - Inches(0.4), Inches(0.35),
             "Algorithm\u202f1  per-cycle parallel IK",
             size=14, bold=True, color=NAVY, font=TITLE_FONT)
    code_lines = [
        "input  : (roll, pitch, yaw), prior q\u207b",
        "output : motor angles q = (q\u2081, q\u2082, q\u2083)",
        "",
        "R\u2090\u2091 \u2190 R\u2098(yaw) R\u1d67(pitch) R\u2093(roll)",
        "for each leg i in {1,2,3}:",
        "    P\u1d62 \u2190 R\u2090\u2091 \u00b7 P\u1d62\u1da0",
        "    f\u1d62(q) \u2190 |P\u1d62 \u2212 A\u1d62(q)| \u2212 L\u1d62",
        "    bracket  \u2190 grid containing q\u207b\u1d62",
        "    q\u1d62  \u2190 bisect(f\u1d62, bracket)",
        "return q",
    ]
    code_box = s.shapes.add_textbox(
        box_x + Inches(0.25), box_y + Inches(0.55),
        box_w - Inches(0.5), box_h - Inches(0.7)
    )
    tf = code_box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(2)
        run = p.add_run()
        run.text = line if line else " "
        run.font.name = MONO_FONT
        run.font.size = Pt(14)
        run.font.color.rgb = NAVY


def slide_pid(prs):
    s = add_blank(prs)
    add_header(s, "Dynamics & Baseline PID",
               "Stiff vs. compliant tuning brackets the AAN operating range")
    w = Inches(6.0)
    add_image(s, os.path.join(FIG, "underdamped_response.png"),
              MARGIN, Inches(1.4), w=w)
    add_caption(s, MARGIN, Inches(4.0), w,
                "Underdamped: Kp = 20, Kd = 0.5, Ki = 1  \u2192  "
                "soft, oscillatory")
    add_image(s, os.path.join(FIG, "critical_response.png"),
              MARGIN + w + Inches(0.3), Inches(1.4), w=w)
    add_caption(s, MARGIN + w + Inches(0.3), Inches(4.0), w,
                "Critically damped: Kp = 50, Kd = 2, Ki = 5  \u2192  "
                "stiff, monotonic")
    add_bullets(s, MARGIN, Inches(4.5), SLIDE_W - 2 * MARGIN, Inches(2.4), [
        "Three independent PID loops on the actuator angles \u03b8\u1d62",
        "Even on a rigid SPM, feedback gains modulate effective compliance",
        "These two regimes bracket the spectrum that the AAN controller "
        "interpolates online",
    ], size=16)


def slide_aan(prs):
    s = add_blank(prs)
    add_header(s, "Assist-As-Needed Control  (proposed)",
               "Patient-torque estimation from motor current, "
               "no distal F/T sensor required")
    add_image(s, os.path.join(FIG, "aan_architecture.png"),
              MARGIN, Inches(1.4), w=Inches(8.0))
    add_caption(s, MARGIN, Inches(5.6), Inches(8.0),
                "AAN architecture (top: gait-phase + asymmetry; "
                "bottom: low-level force tracking)")
    add_bullets(s, Inches(8.6), Inches(1.4),
                SLIDE_W - Inches(8.6) - MARGIN, Inches(5.5), [
        "Estimator:  \u03c4_ext \u2248 K_t \u00b7 I_m \u2212 "
        "\u03c4_model(q, q\u0307, q\u0308_ref)",
        "Assist law:  \u03c4_assist = k_aan(t,e) \u00b7 [\u03c4_ref \u2212 "
        "\u03c4_ext]\u208a",
        "Adaptive gain k_aan grows with tracking error, decays with "
        "successful tracking",
        "Removes need for distal load cell; uses Dynamixel current "
        "feedback",
        "Listed as a planned/proposed contribution \u2014 not yet "
        "deployed on hardware",
    ], size=14)


def slide_hardware(prs):
    s = add_blank(prs)
    add_header(s, "Embedded System & Hardware",
               "Teensy 4.1 master \u00b7 RS-485 bus \u00b7 dual IMU \u00b7 "
               "instrumented gait mat")
    w_h = Inches(5.6)
    add_image(s, os.path.join(FIG, "electronics_breadboard.jpg"),
              MARGIN, Inches(1.4), w=Inches(4.4))
    add_caption(s, MARGIN, Inches(5.85), Inches(4.4),
                "Prototype electronics stack: Teensy 4.1 + IMU + RS-485 "
                "transceiver")
    add_image(s, os.path.join(FIG, "hardware_wiring_diagram.jpg"),
              MARGIN + Inches(4.6), Inches(1.4), w=Inches(4.4))
    add_caption(s, MARGIN + Inches(4.6), Inches(5.85), Inches(4.4),
                "Servo control wiring: Dynamixel + U2D2 + power supply + host")
    add_bullets(s, Inches(9.6), Inches(1.4),
                SLIDE_W - Inches(9.6) - MARGIN, Inches(5.5), [
        "1\u202fkHz control loop on Teensy 4.1",
        "RS-485 daisy chain: 3 \u00d7 XM430-W350-R",
        "Position-control mode + current telemetry",
        "Encoder resolution 0.088\u00b0 / tick",
        "Dual IMU (shank + foot) for absolute reference",
        "Gait mat for stance time, plantar pressure, CoP",
    ], size=13)


def slide_open_source(prs):
    s = add_blank(prs)
    add_header(s, "Open-Source ROS\u202f2 / Gazebo Pipeline",
               "From CAD to closed-loop simulation in three lines")
    add_image(s, os.path.join(FIG, "gazebo_force_torque.png"),
              MARGIN, Inches(1.4), w=Inches(7.4))
    add_caption(s, MARGIN, Inches(6.0), Inches(7.4),
                "Gazebo URDF smoke test: 101\u202fNm pure torque applied "
                "to the proximal link")
    add_text(s, Inches(8.0), Inches(1.4),
             SLIDE_W - Inches(8.0) - MARGIN, Inches(0.4),
             "Repository (MIT licensed):", size=14, bold=True, color=NAVY)
    add_text(s, Inches(8.0), Inches(1.85),
             SLIDE_W - Inches(8.0) - MARGIN, Inches(0.4),
             "github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
             size=12, font=MONO_FONT, color=NAVY)
    add_bullets(s, Inches(8.0), Inches(2.5),
                SLIDE_W - Inches(8.0) - MARGIN, Inches(4.5), [
        "ROS\u202f2 ament_python package",
        "URDF + Xacro, 22 STL meshes, 4 launch files",
        "Parallel-IK solver \u2014 one shared kinematic core",
        "Gazebo verification: sweep force/torque grid \u2192 "
        "no NaN inertias, no mesh interpenetration",
        "Dependency-free closed-loop demo (Python stdlib only)",
        "JSON parameter templates \u2192 swap hardware without "
        "touching Python",
    ], size=13)


def slide_closed_loop_demo(prs):
    s = add_blank(prs)
    add_header(s, "Closed-Loop Tracking Demo  (Algorithm 2)",
               "Reproduces the IK + safety supervisor against the URDF "
               "model")
    box_x = MARGIN
    box_y = Inches(1.4)
    box_w = Inches(7.6)
    box_h = Inches(5.4)
    bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, box_x, box_y,
                            box_w, box_h)
    bg.line.color.rgb = NAVY
    bg.line.width = Pt(1)
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT_GREY
    add_text(s, box_x + Inches(0.2), box_y + Inches(0.1),
             box_w - Inches(0.4), Inches(0.35),
             "Algorithm\u202f2  closed-loop ankle-rehab tracking demo",
             size=14, bold=True, color=NAVY, font=TITLE_FONT)
    code_lines = [
        "parse URDF; pick (j\u2081, j\u2084, j\u2086) as the three "
        "Dynamixel actuators",
        "q \u2190 0;  t \u2190 0",
        "while running:",
        "    \u03c3(t)  \u2190 min(t / Tsoft, 1)            # soft start",
        "    pitch \u2190 \u03c3(t) \u00b7 A_p sin(2\u03c0 f t)",
        "    roll  \u2190 \u03c3(t) \u00b7 A_r sin(2\u03c0 f t)",
        "    q_ref \u2190 ParallelIK(roll, pitch, 0)        # Algo 1",
        "    \u0394q    \u2190 clamp(q_ref \u2212 q,  q\u0307_max \u00b7 \u0394t)",
        "    \u03c4    \u2190 clamp(controller(\u0394q),  \u03c4_max)",
        "    q     \u2190 q + \u0394q                     # virtual actuator",
        "    log(t, q_ref, q, \u03c4, ToTicks(q))           # CSV row",
        "    t     \u2190 t + \u0394t",
    ]
    code_box = s.shapes.add_textbox(
        box_x + Inches(0.25), box_y + Inches(0.55),
        box_w - Inches(0.5), box_h - Inches(0.7)
    )
    tf = code_box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(2)
        run = p.add_run()
        run.text = line if line else " "
        run.font.name = MONO_FONT
        run.font.size = Pt(13)
        run.font.color.rgb = NAVY

    add_bullets(s, Inches(8.4), Inches(1.6),
                SLIDE_W - Inches(8.4) - MARGIN, Inches(5.0), [
        "Reference: \u00b1 12\u00b0 dorsi/plantar, \u00b1 6\u00b0 invert/"
        "evert, 0.05\u202fHz, 3\u202fs ramp",
        "Safety caps: \u03c4 \u2264 1.2\u202fNm,  q\u0307 \u2264 0.8 rad/s",
        "Logs commanded vs. measured q, residual error, Dynamixel ticks",
        "Recorded video shipped in the repo: media/closed_loop_demo.mp4 "
        "(\u224825\u202fMB)",
    ], size=14)


def slide_experiments(prs):
    s = add_blank(prs)
    add_header(s, "Planned Experiments",
               "Quantitative metrics + simulated foot-drop protocol")
    add_text(s, MARGIN, Inches(1.4), Inches(6.0), Inches(0.4),
             "Quantitative metrics", size=16, bold=True)
    add_bullets(s, MARGIN, Inches(1.85), Inches(6.0), Inches(3.0), [
        "Limb Symmetry Index (LSI) \u2014 north-star clinical metric",
        "Jerk = d\u00b3x/dt\u00b3 from foot-plate IMU (smoothness)",
        "Interaction torque \u03c4_int (sensorless estimator, eq. 16)",
        "Center of pressure (CoP) trajectory from gait mat",
        "Human-contribution ratio  \u03b7_h = \u03c4_ext / "
        "(\u03c4_ext + \u03c4_assist)",
    ], size=14)

    add_text(s, Inches(7.2), Inches(1.4), Inches(5.7), Inches(0.4),
             "Four sub-experiments", size=16, bold=True)
    add_bullets(s, Inches(7.2), Inches(1.85), Inches(5.7), Inches(3.0), [
        "E1  Simulated-impairment recovery (controlled foot-drop)",
        "E2  Transparency evaluation (R\u00b2 \u2265 0.95 vs. barefoot)",
        "E3  Active participation under AAN (\u03b7_h trend over sessions)",
        "E4  Passive transfer effect after CPM bout",
    ], size=14)
    add_text(s, MARGIN, Inches(5.0), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Statistics", size=16, bold=True)
    add_bullets(s, MARGIN, Inches(5.45), SLIDE_W - 2 * MARGIN, Inches(2.0), [
        "Within-subject paired t-tests (or Wilcoxon if non-normal); "
        "Bonferroni-Holm correction at the experiment level",
        "Across-session trends: linear mixed-effects model with subject "
        "as a random effect",
        "Bootstrap 95\u202f% CIs (n = 10\u202f000)",
    ], size=14)


def slide_status(prs):
    s = add_blank(prs)
    add_header(s, "Implementation Status",
               "5 of 6 goals delivered; hardware integration in progress")
    rows = [
        ("Wearable 3-RRR mechanism, link ratio \u03c1\u2248 1.15",
         "Completed", "+ ~20 % isotropy index"),
        ("Closed-form & numerical inverse kinematics",
         "Completed", "Algorithm 1, in repo"),
        ("Joint-to-actuator mapping (\u03b8\u1d62 \u2192 XM430 ticks)",
         "Completed", "Sec. VII / Sec. IX"),
        ("Open-source ROS\u202f2 / Gazebo pipeline",
         "Completed", "MIT-licensed release"),
        ("Embedded system architecture",
         "Completed", "Teensy 4.1 + RS-485 + dual IMU"),
        ("AAN control formulation",
         "Proposed", "Eq. (16) \u2013 (18)"),
        ("Hardware integration & subject experiments",
         "In progress", "next phase"),
    ]
    table_x = MARGIN
    table_y = Inches(1.5)
    table_w = SLIDE_W - 2 * MARGIN
    n = len(rows)
    table_h = Inches(0.55) * (n + 1)
    table = s.shapes.add_table(n + 1, 3, table_x, table_y,
                               table_w, table_h).table
    table.columns[0].width = Inches(6.6)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = table_w - Inches(8.6)

    headers = ("Goal", "Status", "Outcome")
    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        para = cell.text_frame.paragraphs[0]
        para.text = ""
        run = para.add_run()
        run.text = h
        run.font.bold = True
        run.font.color.rgb = WHITE
        run.font.name = TITLE_FONT
        run.font.size = Pt(15)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (LIGHT_GREY if r % 2 == 0 else WHITE)
            para = cell.text_frame.paragraphs[0]
            para.text = ""
            run = para.add_run()
            run.text = value
            run.font.name = BODY_FONT
            run.font.size = Pt(13)
            if c == 1:
                run.font.bold = True
                run.font.color.rgb = (
                    NAVY if value == "Completed"
                    else ACCENT if value == "In progress"
                    else GREY
                )


def slide_conclusion(prs):
    s = add_blank(prs)
    add_header(s, "Conclusion & Future Work",
               "What was delivered, what comes next")
    add_text(s, MARGIN, Inches(1.4), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Delivered", size=18, bold=True, color=NAVY)
    add_bullets(s, MARGIN, Inches(1.85), SLIDE_W - 2 * MARGIN, Inches(2.4), [
        "A wearable 3-RRR SPM ankle rehabilitation robot whose remote "
        "center of rotation is anatomically aligned with the talocrural "
        "complex",
        "Closed-form + numerical inverse kinematics that maps "
        "(roll, pitch, yaw) to motor angles in real time",
        "An MIT-licensed ROS\u202f2 / Gazebo design-and-validation "
        "pipeline that any group can clone, build, and extend",
    ], size=15)
    add_text(s, MARGIN, Inches(4.4), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Future work", size=18, bold=True, color=NAVY)
    add_bullets(s, MARGIN, Inches(4.85), SLIDE_W - 2 * MARGIN, Inches(2.2), [
        "Modeling: dual-axis non-concentric ankle model; integrate "
        "Lagrangian dynamics into a feedforward layer",
        "Control & software: instantiate the AAN gain schedule on the "
        "real Dynamixel bus; add gait-phase switching and online "
        "Jacobian-condition monitoring",
        "Experiments: complete healthy-subject protocol with simulated "
        "foot-drop, then plan an IRB-approved patient study",
    ], size=15)


def slide_thanks(prs):
    s = add_blank(prs)
    block = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    block.line.fill.background()
    block.fill.solid()
    block.fill.fore_color.rgb = NAVY
    add_text(s, MARGIN, Inches(2.6), SLIDE_W - 2 * MARGIN, Inches(1.0),
             "Thank you.", size=44, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER)
    add_text(s, MARGIN, Inches(3.7), SLIDE_W - 2 * MARGIN, Inches(0.5),
             "Questions & discussion", size=22, color=ACCENT,
             align=PP_ALIGN.CENTER)
    add_text(s, MARGIN, Inches(4.8), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Yufei Zhang  \u00b7  yz4917@columbia.edu",
             size=16, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, MARGIN, Inches(5.2), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "Advisor: Prof. Sunil K. Agrawal",
             size=14, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, MARGIN, Inches(6.0), SLIDE_W - 2 * MARGIN, Inches(0.4),
             "github.com/YufeiZhang0601/wearable-3rrr-ankle-rehab",
             size=16, color=WHITE, font=MONO_FONT, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    builders = [
        slide_title,
        slide_outline,
        slide_motivation,
        slide_state_of_art,
        slide_anatomy,
        slide_mechanism,
        slide_cad_views,
        slide_singularity,
        slide_kinematics,
        slide_pid,
        slide_aan,
        slide_hardware,
        slide_open_source,
        slide_closed_loop_demo,
        slide_experiments,
        slide_status,
        slide_conclusion,
        slide_thanks,
    ]
    for builder in builders:
        builder(prs)

    total = len(prs.slides)
    for idx, slide in enumerate(prs.slides, start=1):
        if 1 < idx < total:
            add_footer(slide, idx, total)

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    prs.save(OUT_PATH)
    print("wrote {} ({} slides)".format(OUT_PATH, total))


if __name__ == "__main__":
    main()
