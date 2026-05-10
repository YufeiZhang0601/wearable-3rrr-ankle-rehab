# AMR Research Course Report — LaTeX Source

IEEE-style conference paper: *Design and Validation of a Wearable Ankle
Rehabilitation Robot with an Anatomically Aligned 3-RRR Spherical Parallel
Mechanism*. Covers the wearable mechanism, its analytical and numerical
inverse-kinematic models, and the open-source ROS 2 / Gazebo
design-and-validation pipeline released alongside the paper.

## Files

```
report/
├── main.tex          # IEEEtran two-column conference paper
├── references.bib    # BibTeX bibliography
├── figures/          # All figures referenced by main.tex
└── README.md
```

## Compile

### Option A — Overleaf (recommended)

1. Create a new Overleaf project and upload `main.tex`, `references.bib`, and `figures/`.
2. In *Menu → Compiler*, select **pdfLaTeX**.
3. Click **Recompile**. Overleaf will run pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX automatically.

### Option B — Local TeX Live / MiKTeX

```bash
cd report
latexmk -pdf main.tex
```

The output is `main.pdf`.

## Section map

- §I    Introduction
- §II   Related Work
- §III  Mechanism Design and Singularity-Aware Optimization
- §IV   Kinematic Modeling
- §V    Dynamics and Baseline Control
- §VI   Assist-As-Needed Control Strategy *(proposed)*
- §VII  Embedded System and Sensor Architecture
- §VIII **Open-Source Design and Validation Pipeline**
- §IX   Experimental Methodology
- §X    Implementation Status
- §XI   Conclusion and Future Work
