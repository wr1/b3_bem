# Plotter class for b3_bem.

from pathlib import Path
import json
import numpy as np
from .plots import plot_planform, rotorplot, plot_bladeloads, plot_moments


class B3BemPlotter:
    """Plotter for B3 BEM results from JSON."""

    def __init__(self, results_path: Path, run_name: str = None):
        """Load results from JSON file."""
        with open(results_path, "r") as f:
            self.data = json.load(f)
        if "runs" in self.data:
            if run_name is None:
                run_name = list(self.data["runs"].keys())[0]  # Default to first run
            self.run_data = self.data["runs"][run_name]
        else:
            # Backward compatibility
            self.run_data = self.data
        # Convert lists back to arrays
        self.run_data["planform"]["r"] = np.array(self.run_data["planform"]["r"])
        self.run_data["planform"]["chord"] = np.array(
            self.run_data["planform"]["chord"]
        )
        self.run_data["planform"]["twist"] = np.array(
            self.run_data["planform"]["twist"]
        )
        self.run_data["planform"]["thickness"] = np.array(
            self.run_data["planform"]["thickness"]
        )
        self.run_data["performance"]["uinf"] = np.array(
            self.run_data["performance"]["uinf"]
        )
        self.run_data["blade_loads"]["r"] = np.array(self.run_data["blade_loads"]["r"])
        self.run_data["blade_loads"]["combined_rms"] = np.array(
            self.run_data["blade_loads"]["combined_rms"]
        )
        # Convert loads_list back to dicts with arrays
        self.run_data["blade_loads"]["loads_list"] = [
            {k: np.array(v) for k, v in load.items()}
            for load in self.run_data["blade_loads"]["loads_list"]
        ]

    def plot_planform(self, of: Path = Path("ccblade_planform.png")):
        """Plot planform."""
        pf = self.run_data["planform"]
        plot_planform(pf["r"], pf["chord"], pf["twist"], pf["thickness"], of)

    def plot_rotor_performance(self, of: Path = Path("ccblade_out.png")):
        """Plot rotor performance."""
        perf = self.run_data["performance"]
        meta = self.run_data.get("metadata", {})
        rotorplot(
            perf,
            perf["uinf"],
            labels=["P", "CP", "T", "Mb", "omega", "pitch", "tsr", "tip_speed"],
            Uinf_low=meta.get("Uinf_low"),
            Uinf_high=meta.get("Uinf_high"),
            Uinf_switch=meta.get("Uinf_switch"),
            of=of,
        )

    def plot_bladeloads(self, of: Path = Path("ccblade_bladeloads.png")):
        """Plot blade loads."""
        bl = self.run_data["blade_loads"]
        plot_bladeloads(bl["r"], bl["loads_list"], bl["uinf_list"], of)

    def plot_moments(self, of: Path = Path("ccblade_moments.png")):
        """Plot moments."""
        bl = self.run_data["blade_loads"]
        moments_dict = {
            "flapwise": np.array(bl["flapwise_moments"]),
            "edgewise": np.array(bl["edgewise_moments"]),
            "combined_rms": bl["combined_rms"],
        }
        plot_moments(bl["r"], bl["loads_list"], bl["uinf_list"], moments_dict, of)

    def plot_all(self, output_dir: Path = Path(".")):
        """Plot all figures to output_dir."""
        self.plot_planform(output_dir / "ccblade_planform.png")
        self.plot_rotor_performance(output_dir / "ccblade_out.png")
        self.plot_bladeloads(output_dir / "ccblade_bladeloads.png")
        self.plot_moments(output_dir / "ccblade_moments.png")
