# Runner class for b3_bem.

from pathlib import Path
import numpy as np
import pandas as pd
from ccblade.ccblade import CCBlade
import logging
from scipy.interpolate import PchipInterpolator

from ..utils.utils import load_polar, interpolate_polars
from ..plots.plots import plot_planform
from .optimizer import ControlOptimize

logger = logging.getLogger(__name__)


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

        # Plot planform
        plot_planform(r, chord, twist, relative_thickness, self.workdir.parent / "ccblade_planform.png")

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
        self.copt.compute_bladeloads(results)
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
        df = pd.DataFrame(output)
        df.to_csv(self.workdir.parent / "ccblade_output.csv", sep=";")
        from ..plots.plots import rotorplot
        rotorplot(
            output,
            np.array(output['uinf']),
            labels=["P", "CP", "T", "Mb", "omega", "pitch", "tsr", "tip_speed"],
            Uinf_low=self.copt.Uinf_low,
            Uinf_high=self.copt.Uinf_high,
            Uinf_switch=self.copt.Uinf_switch,
            of=self.workdir.parent / "ccblade_out.png",
        )
