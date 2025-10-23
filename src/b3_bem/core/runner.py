# Runner class for b3_bem.

from pathlib import Path
import numpy as np
import pandas as pd
import json
from ccblade.ccblade import CCBlade
import logging
from scipy.interpolate import PchipInterpolator

from ..utils.utils import load_polar, interpolate_polars
from ..plots.planform import plot_planform
from .optimizer import ControlOptimize

logger = logging.getLogger(__name__)


def convert_to_serializable(obj):
    """Convert numpy types to Python serializable types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj


class B3BemRun:
    """Run B3 BEM analysis on a blade."""

    def __init__(self, config: dict, yml_dir: Path):
        """Initialize with a config dict and YAML directory."""
        self.config = config
        self.yml_dir = yml_dir

        # Resolve workdir relative to YAML directory
        workdir_path = Path(self.config["workdir"])
        if not workdir_path.is_absolute():
            workdir_path = self.yml_dir / workdir_path
        self.workdir = workdir_path.resolve() / "mesh"
        self.workdir.mkdir(parents=True, exist_ok=True)  # Ensure mesh directory exists

        bem = self.config["bem"]
        planform = self.config["geometry"]["planform"]

        # Interpolate planform control points using PCHIP
        n_span = 50
        s_span = np.linspace(0, 1, n_span)

        # Chord interpolation
        s_chord = np.array([p[0] for p in planform["chord"]])
        chord_vals = np.array([p[1] for p in planform["chord"]])
        interp_chord = PchipInterpolator(s_chord, chord_vals)
        chord = interp_chord(s_span)

        # Twist interpolation
        s_twist = np.array([p[0] for p in planform["twist"]])
        twist_vals = np.array([p[1] for p in planform["twist"]])
        interp_twist = PchipInterpolator(s_twist, twist_vals)
        twist = interp_twist(s_span)

        # Thickness interpolation
        s_thickness = np.array([p[0] for p in planform["thickness"]])
        thickness_vals = np.array([p[1] for p in planform["thickness"]])
        interp_thickness = PchipInterpolator(s_thickness, thickness_vals)
        relative_thickness = interp_thickness(s_span)

        # z interpolation for radius
        s_z = np.array([p[0] for p in planform["z"]])
        z_vals = np.array([p[1] for p in planform["z"]])
        interp_z = PchipInterpolator(s_z, z_vals)
        z = interp_z(s_span)

        # Radial position
        r = np.abs(z)
        rhub = r[0]
        rtip = r[-1]

        # Control points for plotting
        r_chord = np.abs(interp_z(s_chord))
        r_twist = np.abs(interp_z(s_twist))
        r_thickness = np.abs(interp_z(s_thickness))
        r_z = np.abs(z_vals)
        control_points = {
            'chord': (r_chord, chord_vals),
            'twist': (r_twist, twist_vals),
            'thickness': (r_thickness, thickness_vals),
            'r': (r_z, r_z)
        }

        # Store planform data for output
        self.planform_data = {
            'r': r.tolist(),
            'chord': chord.tolist(),
            'twist': twist.tolist(),
            'thickness': relative_thickness.tolist()
        }

        # Plot planform
        plot_planform(r, chord, twist, relative_thickness, self.workdir.parent / "ccblade_planform.png", control_points)

        if bem["polars"] is None:
            exit("no polars in blade file")
        plrs = sorted(
            [(i['key'], load_polar(yml_dir / Path(i['file']))) for i in bem["polars"]],
            reverse=True,
        )
        iplr = interpolate_polars(
            plrs, relative_thickness, of=self.workdir.parent / "polars.png"
        )
        self.rotor = CCBlade(
            r - r[0],
            chord,
            twist,
            iplr,
            rhub,
            rtip,
            B=bem["B"],
            rho=bem["rho"],
            mu=bem["mu"],
            precone=bem["precone"],
            tilt=bem["tilt"],
            yaw=bem["yaw"],
            shearExp=bem["shearExp"],
            hubHt=bem["hubHt"],
            derivatives=True,
        )
        logger.info(f"Rotor from {rhub} to {rtip}")
        self.copt = ControlOptimize(
            self.rotor,
            bem["max_tipspeed"],
            rtip,
            bem["rated_power"],
            uinf=np.array(bem["uinf"]),
            workdir=self.workdir,
        )

    def run(self) -> None:
        """Execute the B3 BEM analysis."""
        results = self.copt.optimize_all()
        logger.info(f"Number of evaluations per operating point: {[r[9] for r in results]}")
        blade_data = self.copt.compute_bladeloads(results)
        # Prepare output dict
        output = {
            'uinf': [r[0] for r in results],
            'zone': [r[1] for r in results],
            'omega': [r[2] for r in results],
            'pitch': [r[3] for r in results],
            'P': [r[4] for r in results],
            'T': [r[5] for r in results],
            'CT': [r[6] for r in results],
            'CP': [r[7] for r in results],
            'Mb': [r[8] for r in results],
            'niter': [r[9] for r in results],
        }
        # Add TSR
        output['tsr'] = [(omega * 2 * np.pi / 60) * self.copt.rtip / uinf for omega, uinf in zip(output['omega'], output['uinf'])]
        # Add tip speed
        output['tip_speed'] = [omega * 2 * np.pi / 60 * self.copt.rtip for omega in output['omega']]
        
        # Collect all data
        results_data = {
            "config": self.config,
            "planform": self.planform_data,
            "performance": output,
            "blade_loads": blade_data,
            "metadata": {
                "timestamp": str(pd.Timestamp.now()),
                "niter_list": [int(r[9]) for r in results],
                "Uinf_low": float(self.copt.Uinf_low) if self.copt.Uinf_low is not None else None,
                "Uinf_high": float(self.copt.Uinf_high) if self.copt.Uinf_high is not None else None,
                "Uinf_switch": float(self.copt.Uinf_switch) if self.copt.Uinf_switch is not None else None
            }
        }
        
        # Convert to serializable
        results_data = convert_to_serializable(results_data)
        
        # Save to JSON
        output_path = self.workdir.parent / "results.json"
        with open(output_path, "w") as f:
            json.dump(results_data, f, indent=4)
        logger.info(f"Saved results to {output_path}")
