# Fixed run handler for b3_bem.
from pathlib import Path
import numpy as np
import pandas as pd
from ccblade.ccblade import CCBlade
import os
import logging
from contextlib import redirect_stdout, redirect_stderr
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FixedRun:
    """Handle fixed setpoint operations for B3 BEM analysis."""

    def __init__(self, rotor: CCBlade, operation: List[Dict[str, Any]], rtip: float):
        """Initialize with rotor, operation points, and tip radius."""
        self.rotor = rotor
        self.operation = operation
        self.rtip = rtip

    def run(self) -> List[tuple]:
        """Execute the fixed run and return results."""
        results = []
        for op in self.operation:
            with (
                redirect_stdout(open(os.devnull, "w")),
                redirect_stderr(open(os.devnull, "w")),
            ):
                outputs, _ = self.rotor.evaluate(
                    [op["uinf"]], [op["omega"]], [op["pitch"]], coefficients=True
                )
            P = outputs["P"][0]
            T = outputs["T"][0]
            CT = outputs["CT"][0]
            CP = outputs["CP"][0]
            Mb = outputs["Mb"][0]
            results.append(
                (op["uinf"], "fixed", op["omega"], op["pitch"], P, T, CT, CP, Mb, 1)
            )
        logger.info(
            f"Fixed run completed with {len(results)} operating points"
        )
        return results

    def compute_bladeloads(self, results: List[tuple]) -> Dict[str, Any]:
        """Compute blade loads for fixed operation."""
        loads_list = []
        uinf_list = []
        flapwise_moments = []
        edgewise_moments = []
        r = self.rotor.r
        for uinf, _, omega, pitch, _, _, _, _, _, _ in results:
            with (
                redirect_stdout(open(os.devnull, "w")),
                redirect_stderr(open(os.devnull, "w")),
            ):
                loads, _ = self.rotor.distributedAeroLoads(uinf, omega, pitch, 0)
            loads_list.append(loads)
            uinf_list.append(uinf)
            # Compute moments
            Np = loads["Np"]
            Tp = loads["Tp"]
            moment_flap = np.trapezoid(Np * r, r)
            moment_edge = np.trapezoid(Tp * r, r)
            flapwise_moments.append(moment_flap)
            edgewise_moments.append(moment_edge)
        combined_rms = np.sqrt(
            np.array(flapwise_moments) ** 2 + np.array(edgewise_moments) ** 2
        )
        blade_data = {
            "r": r.tolist(),
            "loads_list": [
                {k: v.tolist() for k, v in load.items()} for load in loads_list
            ],
            "uinf_list": uinf_list,
            "flapwise_moments": [float(m) for m in flapwise_moments],
            "edgewise_moments": [float(m) for m in edgewise_moments],
            "combined_rms": combined_rms.tolist(),
        }
        return blade_data
