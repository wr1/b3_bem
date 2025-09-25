#set page(margin: 1in)
#set text(font: "New Computer Modern", size: 12pt)
#set heading(numbering: "1.")

= Technical Brief: B3 BEM Codebase

== Introduction

The `b3_bem` project implements a Blade Element Momentum (BEM) analysis tool for wind turbine rotor performance, leveraging the CCBlade library for aerodynamic computations. It supports configuration via YAML files, optimization of control parameters (e.g., tip-speed ratio, pitch), and generation of performance metrics, blade loads, and visualizations. The codebase integrates with Statesman for workflow management and provides a CLI for execution.

Key features include:
- Interpolation of airfoil polars based on blade thickness.
- Rotor performance evaluation across wind speeds.
- Optimization for below- and above-rated conditions.
- Output of CSV tables and plots (e.g., power curves, blade loads, moments).
- Modular design with utilities for data loading and plotting.

The project follows Python best practices (PEP 8) and uses modern tools like Pydantic for validation, Ruamel.yaml for portable YAML handling, and Treeparse for CLI parsing.

== Architecture Overview

The codebase is organized into subdirectories under `src/b3_bem/`:

- `core/`: Core logic for BEM analysis and optimization.
  - `step.py`: Statesman-integrated step for executing analysis, handling dependencies and outputs.
  - `runner.py`: `B3BemRun` class orchestrates CCBlade setup, polar interpolation, and control optimization.
  - `optimizer.py`: `RotorOptimizer` and `ControlOptimize` classes for fine-tuning pitch and TSR using SciPy's `fmin`.
  - `ccblade.py`: Placeholder for CCBlade-specific extensions (currently minimal).

- `utils/`: Reusable functions.
  - `utils.py`: Polar loading, interpolation (PCHIP), TSR/omega conversions, and optimization helpers.
  - `loft_utils.py`: Airfoil coordinate loading from files, with optional normalization.

- `cli/`: Command-line interface.
  - `cli.py`: Treeparse-based CLI with `run` command for YAML-driven analysis (options: --yml/-y, --force/-f).
  - `yml_portable.py`: YAML parsing with Pydantic models (`Config`, `Aero`) to embed airfoil data inline, avoiding external file dependencies.

- `plots/`: Visualization utilities.
  - `plots.py`: Functions for polars, blade loads, moments, and rotor performance plots using Matplotlib.

- Root: `pyproject.toml` for build (Hatchling), dependencies (NumPy, Pandas, SciPy, CCBlade, etc.), and CLI entrypoint (`b3-bem` script).
- `examples/`: `ex1.py` demonstrates programmatic usage via `B3BemStep`.

Data flow:
1. Load YAML config (portable airfoils).
2. Interpolate planform (chord, twist, thickness) and polars.
3. Initialize CCBlade rotor.
4. Optimize controls (below-rated TSR/pitch, above-rated pitch feathering).
5. Compute loads/moments and save outputs (CSV, PNG).

== Dependencies

- Core: NumPy, Pandas, SciPy, Matplotlib, CCBlade (aerodynamics).
- Config/CLI: Ruamel.yaml, Pydantic, Treeparse, Rich (progress).
- Workflow: Statesman (git+https://github.com/wr1/statesman.git).
- Build: Hatchling; optional local CCBlade path.

All are pinned in `pyproject.toml`. No runtime internet required post-install.

== Key Algorithms

- `Polar Interpolation`: Load polars from files, interpolate Cl/Cd/Cm to blade-relative thickness using linear interp; create `CCAirfoil` list.
- `Planform Interpolation`: PCHIP on control points for chord/twist/thickness to 50-spanwise stations.
- `Optimization`:
  - Below-rated: Minimize power error to rated via `fmin` on (omega, pitch).
  - Above-rated: Fixed TSR, adjust pitch per wind speed bin to cap power.
- `Loads`: Distributed aero loads via CCBlade; integrate for moments (trapezoidal rule).
- `Plots`: Subplot grids for multi-operating-point data; RMS combined moments.

Assumptions: Hub radius ~1m, tip ~60m; wind speeds from config (`bem.uinf`); rated power 20MW default.

== Usage

CLI: `b3-bem run --yml config.yml [--force]`

YAML structure (`Config` model):
- `general`: Metadata.
- `geometry.planform`: Control points [s, value] for chord/twist/thickness.
- `aero.airfoils`: List with keys/files or inline XY.
- `bem`: B (blades), rho, uinf array, rated_power, max_tipspeed, polars refs.

Programmatic:
```python
import from b3_bem.core.step import B3BemStep
step = B3BemStep('config.yml', force=True)
step.run()
```

Outputs in `workdir/mesh/` (relative to YAML): `ccblade_output.csv` (performance), `ccblade_bladeloads.csv` (Np/Tp), `ccblade_moments.csv` (root moments), plots (PNG).

== Limitations and Future Work

- Fixed spanwise discretization (50 stations); configurable?
- No derivatives in CCBlade (set False); enable for sensitivity?
- Assumes constant rho/mu; add shear profile support.
- YAML portability embeds airfoils but assumes simple formats; extend for lofting.
- Testing: Add pytest suite for utils/optimizer.
- Performance: Vectorize evaluations; cache more aggressively.

This brief captures the v0.1.0 state; modular design facilitates extensions (e.g., multi-blade, fatigue).