# Optimizer classes for b3_bem.

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize, brentq
import multiprocessing as mp
from ccblade.ccblade import CCBlade
import os
import logging
from contextlib import redirect_stdout, redirect_stderr
from rich.progress import Progress
from scipy.integrate import trapezoid

from ..plots.bladeloads import (
    plot_bladeloads,
    plot_moments,
)

logger = logging.getLogger(__name__)


class ControlOptimize:
    """Optimize rotor control settings using gradient-based approach with 4 regimes."""

    def __init__(
        self,
        rotor: CCBlade,
        max_tipspeed: float,
        rtip: float,
        rating: float,
        uinf: np.ndarray,
        workdir: Path,
        serial: bool = False,
    ):
        """Initialize control optimizer with rotor parameters."""
        self.rotor = rotor
        self.max_tipspeed = max_tipspeed
        self.rating = rating
        self.uinf = uinf
        self.rtip = rtip
        self.workdir = workdir
        self.serial = serial
        self.omega_min = 2  # RPM, adjust as needed
        self.omega_max = self.max_tipspeed * 60 / (2 * np.pi * self.rtip)  # RPM
        self.pitch_min = -1.5
        self.pitch_max = 80
        self.Omega_opt = 5.0  # Initial guess
        self.pitch_opt = 0.0  # Initial guess
        self.Uinf_low = None
        self.Uinf_high = None
        self.Uinf_switch = None

    def optimize_low(self, Uinf):
        """Optimize for low wind speeds: fixed omega_min, optimize pitch."""
        Omega = self.omega_min
        initial_guess_pitch = [self.pitch_opt]

        def obj(pitch):
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch])
            return -outputs["P"][0]

        res = minimize(obj, initial_guess_pitch, bounds=[(self.pitch_min, self.pitch_max)])
        pitch_opt_res = res.x[0]
        with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
            outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch_opt_res], coefficients=True)
        P = outputs["P"][0]
        T = outputs["T"][0]
        CT = outputs["CT"][0]
        CP = outputs["CP"][0]
        Mb = outputs["Mb"][0]
        return Omega, pitch_opt_res, P, T, CT, CP, Mb, res.nfev

    def optimize_mid(self, Uinf):
        """Optimize for mid wind speeds: optimize omega and pitch."""
        Omega_est = self.Omega_opt * (Uinf / 6.0)
        initial_guess = [Omega_est, self.pitch_opt]

        def obj(x):
            Omega, pitch = x
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch])
            return -outputs["P"][0]

        res = minimize(obj, initial_guess, bounds=[(self.omega_min, self.omega_max), (self.pitch_min, self.pitch_max)])
        Omega_opt_res, pitch_opt_res = res.x
        with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
            outputs, _ = self.rotor.evaluate(
                [Uinf], [Omega_opt_res], [pitch_opt_res], coefficients=True
            )
        P = outputs["P"][0]
        T = outputs["T"][0]
        CT = outputs["CT"][0]
        CP = outputs["CP"][0]
        Mb = outputs["Mb"][0]
        return Omega_opt_res, pitch_opt_res, P, T, CT, CP, Mb, res.nfev

    def optimize_upper(self, Uinf):
        """Optimize for upper wind speeds: fixed omega_max, optimize pitch."""
        Omega = self.omega_max
        initial_guess_pitch = [self.pitch_opt]

        def obj(pitch):
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch])
            return -outputs["P"][0]

        res = minimize(obj, initial_guess_pitch, bounds=[(self.pitch_min, self.pitch_max)])
        pitch_opt_res = res.x[0]
        with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
            outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch_opt_res], coefficients=True)
        P = outputs["P"][0]
        T = outputs["T"][0]
        CT = outputs["CT"][0]
        CP = outputs["CP"][0]
        Mb = outputs["Mb"][0]
        return Omega, pitch_opt_res, P, T, CT, CP, Mb, res.nfev

    def optimize_high(self, Uinf):
        """Optimize for high wind speeds: fixed omega_max, find pitch for rated power."""
        Omega = self.omega_max
        initial_guess_pitch = [self.pitch_opt]

        def func(pitch):
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch])
            return outputs["P"][0] - self.rating

        try:
            pitch_opt_res, r = brentq(func, self.pitch_min, self.pitch_max, full_output=True)
            niter = r.iterations
        except ValueError:
            # If rating not reached, maximize P instead
            def obj(pitch):
                with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                    outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch])
                return -outputs["P"][0]

            res = minimize(obj, initial_guess_pitch, bounds=[(self.pitch_min, self.pitch_max)])
            pitch_opt_res = res.x[0]
            niter = res.nfev
        with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
            outputs, _ = self.rotor.evaluate([Uinf], [Omega], [pitch_opt_res], coefficients=True)
        P = outputs["P"][0]
        T = outputs["T"][0]
        CT = outputs["CT"][0]
        CP = outputs["CP"][0]
        Mb = outputs["Mb"][0]
        return Omega, pitch_opt_res, P, T, CT, CP, Mb, niter

    def initialize_optimal(self):
        """Compute optimal at reference wind speed (6 m/s) to get initial estimates."""
        ref_uinf = 6.0
        if ref_uinf not in self.uinf:
            # Find closest
            ref_uinf = self.uinf[np.argmin(np.abs(self.uinf - ref_uinf))]
        self.Omega_opt, self.pitch_opt, _, _, _, _, _, _ = self.optimize_mid(ref_uinf)
        tsr_opt = self.Omega_opt * self.rtip / ref_uinf
        self.Uinf_low = self.omega_min * self.rtip / tsr_opt
        self.Uinf_high = self.omega_max * self.rtip / tsr_opt

        # Find Uinf_switch
        def P_at_max_omega_pitch0(Uinf):
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [self.omega_max], [0], coefficients=True)
            return outputs["P"][0] - self.rating

        try:
            self.Uinf_switch, _ = brentq(P_at_max_omega_pitch0, self.Uinf_high, max(self.uinf), full_output=True)
        except ValueError:
            self.Uinf_switch = max(self.uinf)

    def process_Uinf(self, Uinf):
        """Process a single wind speed, assign zone and optimize."""
        if Uinf < self.Uinf_low:
            zone = "low"
            Omega, pitch, P, T, CT, CP, Mb, niter = self.optimize_low(Uinf)
        elif Uinf <= self.Uinf_high:
            zone = "mid"
            Omega, pitch, P, T, CT, CP, Mb, niter = self.optimize_mid(Uinf)
        else:
            # Check if P at omega_max with pitch=0 > rating
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                outputs, _ = self.rotor.evaluate([Uinf], [self.omega_max], [0], coefficients=True)
            if outputs["P"][0] > self.rating:
                zone = "high"
                Omega, pitch, P, T, CT, CP, Mb, niter = self.optimize_high(Uinf)
            else:
                zone = "upper"
                Omega, pitch, P, T, CT, CP, Mb, niter = self.optimize_upper(Uinf)
        return Uinf, zone, Omega, pitch, P, T, CT, CP, Mb, niter

    def optimize_all(self):
        """Run optimization for all wind speeds using multiprocessing or serial."""
        self.initialize_optimal()
        if self.serial:
            results = [self.process_Uinf(u) for u in self.uinf]
        else:
            with Progress() as progress:
                task = progress.add_task("Optimizing operating points...", total=len(self.uinf))
                results = []
                with mp.Pool() as pool:
                    for result in pool.imap(self.process_Uinf, self.uinf):
                        results.append(result)
                        progress.update(task, advance=1)
        return results

    def compute_bladeloads(self, results):
        """Compute and return blade loads and moments data."""
        loads_list = []
        uinf_list = []
        flapwise_moments = []
        edgewise_moments = []
        r = self.rotor.r
        for uinf, _, omega, pitch, _, _, _, _, _, _ in results:
            with redirect_stdout(open(os.devnull, "w")), redirect_stderr(open(os.devnull, "w")):
                loads, _ = self.rotor.distributedAeroLoads(uinf, omega, pitch, 0)
            loads_list.append(loads)
            uinf_list.append(uinf)
            # Compute moments
            Np = loads['Np']
            Tp = loads['Tp']
            moment_flap = trapezoid(Np * r, r)
            moment_edge = trapezoid(Tp * r, r)
            flapwise_moments.append(moment_flap)
            edgewise_moments.append(moment_edge)
        combined_rms = np.sqrt(np.array(flapwise_moments)**2 + np.array(edgewise_moments)**2)
        blade_data = {
            'r': r.tolist(),
            'loads_list': [{k: v.tolist() for k, v in load.items()} for load in loads_list],
            'uinf_list': uinf_list,
            'flapwise_moments': [float(m) for m in flapwise_moments],
            'edgewise_moments': [float(m) for m in edgewise_moments],
            'combined_rms': combined_rms.tolist()
        }
        return blade_data
