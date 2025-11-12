#!/usr/bin/env python3
"""Programmatic example of running B3 BEM analysis with planform defined in code."""

from pathlib import Path
import tempfile
import logging
from rich.logging import RichHandler
from b3_bem.core.step import B3BemStep
from b3_bem.cli.yml_portable import save_yaml, Config
from b3_bem.plots.plotter import B3BemPlotter

# Set up logging with Rich formatting
logging.basicConfig(
    level=logging.INFO, handlers=[RichHandler(show_time=False)], format="%(message)s"
)

# Define config programmatically
config = {
    "workdir": "temp_blade",
    "geometry": {
        "planform": {
            "npchord": 200,
            "npspan": 200,
            "pre_rotation": -90,
            "z": [[0, -3], [1, -126]],
            "chord": [
                [0.0, 5],
                [0.03, 5.06],
                [0.2, 6.5],
                [0.4, 4.4],
                [0.6, 2.8],
                [0.75, 2.0],
                [0.94, 1.4],
                [0.985, 0.8],
                [1, 0.1],
            ],
            "thickness": [
                [0.0, 1.0],
                [0.05, 0.97],
                [0.2, 0.53],
                [0.31, 0.39],
                [1.0, 0.17],
            ],
            "twist": [
                [0.0, 10],
                [0.2, 2],
                [0.4, 1],
                [0.6, 0],
                [0.8, -0.5],
                [0.9, -1],
                [1.0, 0],
            ],
        }
    },
    "bem": {
        "rated_power": 10000000,
        "polars": [
            {"key": 1.0, "name": "Cylinder", "file": str(Path(__file__).parent / "polars" / "Cylinder1.dat")},
            {"key": 0.21, "name": "DU21", "file": str(Path(__file__).parent / "polars" / "DU21_A17.dat")},
            {"key": 0.25, "name": "DU25", "file": str(Path(__file__).parent / "polars" / "DU25_A17.dat")},
            {"key": 0.30, "name": "DU30", "file": str(Path(__file__).parent / "polars" / "DU30_A17.dat")},
            {"key": 0.35, "name": "DU35", "file": str(Path(__file__).parent / "polars" / "DU35_A17.dat")},
            {"key": 0.40, "name": "DU40", "file": str(Path(__file__).parent / "polars" / "DU40_A17.dat")},
            {"key": 0.17, "name": "NACA64", "file": str(Path(__file__).parent / "polars" / "NACA64_A17.dat")},
        ],
        "B": 3,
        "rho": 1.225,
        "mu": 0.0000181,
        "precone": 0,
        "tilt": 0,
        "yaw": 0,
        "shearExp": 0.2,
        "hubHt": 120,
        "max_tipspeed": 95,
        "uinf": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20],
    },
}

# Create Config object
config_obj = Config(**config)

# Create a temporary YAML file
with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
    save_yaml(Path(f.name), config_obj)
    config_path = f.name

# Create and run the step with force=True
step = B3BemStep(config_path, force=True)
step.run()

# Generate plots
results_path = Path(config_path).parent / step.config["workdir"] / "results.json"
plotter = B3BemPlotter(results_path)
plotter.plot_all(Path(config_path).parent / step.config["workdir"])

logging.info("B3 BEM analysis and plotting completed with programmatic config.")
