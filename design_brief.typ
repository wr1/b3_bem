# B3 BEM Codebase Brief

== Overview

The B3 BEM project implements a Blade Element Momentum (BEM) analysis tool for wind turbine rotor performance. It leverages the CCBlade library for aerodynamic computations, supports configuration via YAML files, and integrates with Statesman for workflow management. The tool optimizes control parameters like tip-speed ratio and pitch, generates performance metrics, blade loads, and visualizations, and provides a CLI for execution.

== Key Features

- *YAML Configuration*: Portable config loading with embedded airfoil data.
- *Optimization*: Gradient-based approach using CCBlade gradients for 4-regime control optimization (low, mid, upper, high wind speeds).
- *Multiprocessing*: Parallel processing for optimization across wind speeds.
- *Visualization*: Plots for planform, polars, blade loads, moments, and rotor performance.
- *Integration*: Statesman for workflow steps, CLI via treeparse.

== Recent Refactor

- Preserved plotting, planform interpolation (PCHIP), and thickness interpolation.
- Transitioned to gradient-based optimization inspired by CCBlade's grad6.py.
- Implemented 4-regime optimization with initial guesses from reference wind speed (6 m/s).
- Added multiprocessing for efficient computation.
- Uses optimized solutions as initial points for subsequent optimizations.

== Project Structure

- `src/b3_bem/`: Core modules.
  - `cli/`: Command-line interface (yml_portable.py, cli.py).
  - `core/`: Runner (runner.py), optimizer (optimizer.py), step (step.py).
  - `plots/`: Plotting functions (plots.py).
  - `utils/`: Utilities (utils.py, loft_utils.py).
- `tests/`: Unit tests (test_optimizer.py, test_utils.py).
- `examples/`: Example scripts (ex1.py).
- `pyproject.toml`: Project configuration with dependencies and scripts.

== Usage

Run via CLI: `b3-bem --yml <config.yml>` or programmatically with `B3BemStep`.

Dependencies: numpy, pandas, matplotlib, scipy, CCBlade, rich, statesman, treeparse, ruamel.yaml, pydantic.

== Status

Codebase is modular, follows PEP 8, uses vectorization with numpy, validation with pydantic, and is ready for further development or deployment.