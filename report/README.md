# AMR Course Report — LaTeX Source

Professional IEEE-style report for the AMR Research Course, structured around
the 3-RRR ankle rehabilitation robot project. The content integrates:

- the prior arXiv paper (`rehabilitation-robot.pdf`) on structural design,
  kinematics, dynamics, and PID simulation,
- the project status memo (`Roar.docx`), covering singularity-aware structural
  optimization, the AAN control strategy, the experimental protocol, and the
  hardware/sensor architecture,
- the present semester software pipeline (STEP feature extraction, numerical
  IK, ROS 2/RViz demo, and Dynamixel tick output).

## Files

```
report_latex/
├── main.tex          # IEEEtran two-column conference paper
├── references.bib    # BibTeX bibliography
├── figures/          # Place figures here (CAD, RViz, plots)
└── README.md
```

## Compile

### Option A — Overleaf (recommended)

1. Create a new Overleaf project.
2. Upload `main.tex`, `references.bib`, and the `figures/` folder.
3. In *Menu → Compiler*, select **pdfLaTeX**.
4. Click **Recompile**. Overleaf will run pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX automatically.

### Option B — Local TeX Live / MiKTeX

```bash
cd report_latex
latexmk -pdf main.tex
```

or manually:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The output is `main.pdf`.

## Before Submission Checklist

1. Replace placeholder figures in `figures/` with:
   - `cad-prototype.pdf` — 3-RRR mechanism schematic + CAD render + 3D-printed
     prototype photo.
   - `rviz-demo.pdf` — RViz screenshot of `parallel_ik_pose_demo`.
   - Optionally a singularity-distribution / workspace-comparison figure
     before vs. after the link-ratio optimization.
2. Confirm the author block in `main.tex` matches your final author list and
   advisor.
3. Optionally adjust the abstract numerical example to match the latest IK
   parameter file.
4. Recompile and verify all references resolve (no `?` in the PDF).

## Section Map (for skimming)

- §I  Introduction
- §II Mechanism Design and Structural Optimization (singularity, l2/l1≈1.15)
- §III Kinematic Modeling (analytical IK + numerical IK)
- §IV Dynamics and Baseline Control (Lagrangian + PID)
- §V Assist-As-Needed Control Strategy (AAN, current-based torque estimation)
- §VI Software and ROS 2 Implementation (auto params + RViz demo)
- §VII Hardware and Sensor Architecture (Raspberry Pi + RS485 + dual IMU)
- §VIII Experimental Protocol (LSI, jerk, transparency, transfer)
- §IX Current Results and Seven-Week Milestones
- §X Conclusion and Future Work
