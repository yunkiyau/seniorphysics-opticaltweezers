# Optical Tweezers Brownian Motion Analysis

This project analyses microscopic bead motion recorded with a Thorlabs portable optical-tweezers setup at the University of Sydney. I used Blender to track beads in microscope video, exported the tracked positions with an open-source add-on, and developed a Python notebook to convert the coordinates into physical measurements and compare the motion of 1 µm and 3 µm beads.

Blender provides the tracking functionality; this repository contains my downstream analysis, not a tracking algorithm written from scratch.

## Workflow

1. Record microscope video (1280 × 1024, 15 frames per second in this experiment).
2. Track bead positions in Blender 2.8 and export trajectories using [blenderMotionExport](https://github.com/Amudtogal/blenderMotionExport).
3. Load the semicolon-delimited `frame;x;y` CSV files into Python.
4. Convert pixels to micrometres using 11.66 pixels/µm, based on a 3 µm bead diameter.
5. Calculate squared displacement from each trajectory's initial position, then its cumulative mean and the average across beads of the same size.
6. Plot trajectories and fit displacement trends with a straight line, including the fitted intercept.

The calculation retains the original experiment's cumulative displacement definition. It is not the usual time-lag-averaged mean-squared-displacement estimator. Tracks within a size group are truncated to the shortest track and aligned by elapsed time since each track starts, not by their absolute frame numbers.

## Included files

```text
notebooks/BrownianMotionAnalysis.ipynb  Analysis and plots
data/                                 Ten exported Brownian-motion tracks
tests/test_analysis.py                Numerical and run-all regression checks
```

The microscope videos, Blender project and separate trapped-bead recording are not included. You can run the Brownian-motion analysis using the supplied CSVs without Blender or microscope hardware.

## Setup and use

Use Python 3.10 or later. From the repository root:

```bash
python -m pip install numpy matplotlib jupyter
jupyter notebook notebooks/BrownianMotionAnalysis.ipynb
```

Run all cells. The notebook finds `data/` when launched from the repository root or `notebooks/`. If using a different working directory, set `DATA_DIR` in the first code cell to the repository's data directory. In Colab, clone or upload the repository, keep its directory structure, and change into its root before running.

CSV rows must contain finite coordinates and consecutive integer frame numbers. Missing frames raise an explicit error because the analysis assumes one row per frame; do not remove gaps silently. The supplied tracks satisfy this requirement, including the track whose first frame is 936.

## Corrections to the historical notebook

The corrected notebook preserves the raw measurements and does not revise the original report. Previous source and saved outputs remain available in Git history.

- Replaced hard-coded Colab `/content/` paths with repository-relative data discovery.
- Matched the time axis to the displacement samples: the first displacement after the reference frame occurs at `1 / FPS`, not zero.
- Kept the fitted intercept in regression predictions, residuals, R² calculations and plotted lines. The regression is an unconstrained straight-line fit, not a fit forced through the origin.
- Corrected speed conversion to `distance_um × FPS × 1e-6` metres per second. The old expression incorrectly placed the frame rate inside the square root. At 15 FPS, this correction alone increases speeds by √15 for the same track.
- Removed stale saved outputs and hard-coded force/uncertainty results. Rerun the cells to generate current plots and statistics.
- Made the missing trapped-bead analysis optional, with an explicit skip message.

These corrections can change figures and numerical results relative to the historical report. They are software corrections, not a new validation of the experiment.

## Optional trapped-bead calculation

The notebook references `data/laser4_Held_bead.csv`, which is not supplied. If you have the original file, place it there in the same `frame;x;y` format. The optional cells then calculate frame-to-frame speed and a Stokes-force estimate using the historical viscosity value (570.38 × 10⁻⁶ Pa·s) and bead radius (1.5 µm).

Without that recording, the force result cannot be reproduced or validated. Do not substitute one of the freely moving Brownian tracks. The historical viscosity is an explicit input, not a freshly calibrated value or proof that the resulting force is accurate.

## Limitations

- The calibration of 11.66 pixels/µm and 15 FPS are specific to this experiment.
- Pixel calibration, localisation, timing, bead-size and viscosity uncertainties have not been propagated through the complete analysis.
- Cumulative displacement observations are correlated. The notebook's ordinary-least-squares standard errors and nominal 1.96× values are descriptive; they are not validated confidence intervals for the physical parameters.
- The analysis is an educational research workflow, not a general-purpose particle-tracking or validated force-calibration package.

## Regression checks

After installing the dependencies, run:

```bash
python -m unittest discover -s tests -v
```

The checks cover speed units, stationary particles, displacement averaging, regression intercepts and time origin, CSV calibration/frame validation, and execution of all code cells with the included data from both supported working directories. They do not require hardware or establish the validity of the original experiment.

## Author and attribution

Analysis workflow: Yunki Yau, University of Sydney Senior Physics laboratory project, 2024.

Motion tracking: Blender; CSV export: the independently developed [blenderMotionExport](https://github.com/Amudtogal/blenderMotionExport) add-on.

Questions: yunki.yau@gmail.com.
