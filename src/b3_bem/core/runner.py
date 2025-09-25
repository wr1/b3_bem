# Runner class for b3_bem.

from pathlib import Path
import numpy as np
import pandas as pd
from ccblade.ccblade import CCBlade
import os
import logging
from typing import List, Tuple, Dict, Optional, Any
from scipy.interpolate import PchipInterpolator

from ..utils.utils import load_polar, interpolate_polars
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
        rtip = 60.0  # Assume rtip
        rhub = 1.0
        r = s_span * (rtip - rhub) + rhub

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
            derivatives=False,
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
        self.copt.control_opt_below_rated()
        output = self.copt.control_opt_above_rated()
        self.copt.compute_bladeloads()
        del output["W"]
        df = pd.DataFrame(output).dropna()
        df.to_csv(self.workdir.parent / "ccblade_output.csv", sep=";")
