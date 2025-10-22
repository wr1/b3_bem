# Plotter class for b3_bem.

from pathlib import Path
import json
import numpy as np
from .plots import plot_planform, rotorplot, plot_bladeloads, plot_moments


class B3BemPlotter:
    """Plotter for B3 BEM results from JSON."""

    def __init__(self, results_path: Path):
        """Load results from JSON file."""
        with open(results_path, "r") as f:
            self.data = json.load(f)
        # Convert lists back to arrays
        self.data["planform"]["r"] = np.array(self.data["planform"]["r"])
        self.data["planform"]["chord"] = np.array(self.data["planform"]["chord"])
        self.data["planform"]["twist"] = np.array(self.data["planform"]["twist"])
        self.data["planform"]["thickness"] = np.array(self.data["planform"]["thickness"])
        self.data["performance"]["uinf"] = np.array(self.data["performance"]["uinf"])
        self.data["blade_loads"]["r"] = np.array(self.data["blade_loads"]["r"])
        self.data["blade_loads"]["combined_rms"] = np.array(self.data["blade_loads"]["combined_rms"])
        # Convert loads_list back to dicts with arrays
        self.data["blade_loads"]["loads_list"] = [
            {k: np.array(v) for k, v in load.items()} for load in self.data["blade_loads"]["loads_list"]
        ]

    def plot_planform(self, of: Path = Path("ccblade_planform.png")):
        """Plot planform."""
        pf = self.data["planform"]
        plot_planform(pf["r"], pf["chord"], pf["twist"], pf["thickness"], of)

    def plot_rotor_performance(self, of: Path = Path("ccblade_out.png")):
        """Plot rotor performance."""
        perf = self.data["performance"]
        meta = self.data["metadata"]
        rotorplot(
            perf,
            perf["uinf"],
            labels=["P", "CP", "T", "Mb", "omega", "pitch", "tsr", "tip_speed"],
            Uinf_low=meta["Uinf_low"],
            Uinf_high=meta["Uinf_high"],
            Uinf_switch=meta["Uinf_switch"],
            of=of,
        )

    def plot_bladeloads(self, of: Path = Path("ccblade_bladeloads.png")):
        """Plot blade loads."""
        bl = self.data["blade_loads"]
        plot_bladeloads(bl["r"], bl["loads_list"], bl["uinf_list"], of)

    def plot_moments(self, of: Path = Path("ccblade_moments.png")):
        """Plot moments."""
        bl = self.data["blade_loads"]
        moments_dict = {
            "flapwise": np.array(bl["flapwise_moments"]),
            "edgewise": np.array(bl["edgewise_moments"]),
            "combined_rms": bl["combined_rms"]
        }
        plot_moments(bl["r"], bl["loads_list"], bl["uinf_list"], moments_dict, of)

    def plot_all(self, output_dir: Path = Path(".")):
        """Plot all figures to output_dir."""
        self.plot_planform(output_dir / "ccblade_planform.png")
        self.plot_rotor_performance(output_dir / "ccblade_out.png")
        self.plot_bladeloads(output_dir / "ccblade_bladeloads.png")
        self.plot_moments(output_dir / "ccblade_moments.png")
