# Plotting functions for b3_bem.

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import math
import logging
from typing import List, Tuple, Dict, Optional, Any

logger = logging.getLogger(__name__)


def plot_planform(r, chord, twist, thickness, of: Path = Path("ccblade_planform.png"), control_points: Optional[Dict[str, Tuple[np.ndarray, np.ndarray]]] = None) -> None:
    """Plot planform data: chord, twist, thickness, radius."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs[0, 0].plot(r, chord)
    axs[0, 0].set_title('Chord (m)')
    axs[0, 0].set_xlabel('r (m)')
    axs[0, 0].grid()
    if control_points and 'chord' in control_points:
        r_pts, vals = control_points['chord']
        axs[0, 0].scatter(r_pts, vals, color='red', marker='o', s=20)
    axs[0, 1].plot(r, twist)
    axs[0, 1].set_title('Twist (deg)')
    axs[0, 1].set_xlabel('r (m)')
    axs[0, 1].grid()
    if control_points and 'twist' in control_points:
        r_pts, vals = control_points['twist']
        axs[0, 1].scatter(r_pts, vals, color='red', marker='o', s=20)
    axs[1, 0].plot(r, thickness)
    axs[1, 0].set_title('Relative Thickness')
    axs[1, 0].set_xlabel('r (m)')
    axs[1, 0].grid()
    if control_points and 'thickness' in control_points:
        r_pts, vals = control_points['thickness']
        axs[1, 0].scatter(r_pts, vals, color='red', marker='o', s=20)
    axs[1, 1].plot(r, r)
    axs[1, 1].set_title('Radius (m)')
    axs[1, 1].set_xlabel('r (m)')
    axs[1, 1].grid()
    if control_points and 'r' in control_points:
        r_pts, vals = control_points['r']
        axs[1, 1].scatter(r_pts, vals, color='red', marker='o', s=20)
    fig.tight_layout()
    fig.savefig(of)
    plt.close(fig)
    logger.info(f"Saved {of}")


def plot_interpolated_polars(
    t: List[float], data: np.ndarray, of: Path = Path("polars.png")
) -> None:
    """Plot interpolated polars with thickness values."""
    fig, ax = plt.subplots(3, 1, figsize=(16, 25))
    for n, i in enumerate(t):
        alpha, cl, cd, cm = data[:, :, n]
        ax[0].plot(alpha, cl, label=f"t={t[n]:.3f}")
        ax[1].plot(alpha, cd)
        ax[2].plot(cd, cl)
        ax[0].set_ylabel("Cl")
        ax[1].set_ylabel("Cd")
        ax[2].set_ylabel("Cm")
        ax[0].grid()
        ax[1].grid()
        ax[2].grid()
    fig.tight_layout()
    fig.savefig(of)


def plot_polars(polars: List[tuple], of: Path = Path("polars_in.png")) -> None:
    """Plot polar data from a list."""
    fig, ax = plt.subplots(3, 1, figsize=(16, 20))
    for i in polars:
        alpha, cl, cd, cm = i[1]
        ax[0].plot(alpha, cl, label=i[0])
        ax[1].plot(alpha, cd)
        ax[2].plot(cd, cl)
        ax[0].set_ylabel("Cl")
        ax[1].set_ylabel("Cd")
        ax[2].set_ylabel("Cl - Cd")
        ax[0].legend()
        ax[0].grid()
        ax[1].grid()
        ax[2].grid()
    fig.tight_layout()
    fig.savefig(of)


def plot_grid(
    num_plots: int, figsize: tuple = (15, 15)
) -> Tuple[plt.Figure, np.ndarray]:
    """Create a grid of subplots for plotting."""
    grid_size = math.isqrt(num_plots)
    columns = grid_size
    rows = np.ceil(num_plots / grid_size).astype(int)
    fig, axs = plt.subplots(rows, columns, figsize=figsize)
    axs = axs.flatten()
    for idx in range(len(axs) - 1, rows * columns):
        fig.delaxes(axs[idx])
    return fig, axs


def plot_bladeloads(
    r: np.ndarray, loads_list: List[Dict[str, np.ndarray]], uinf_list: List[float], of: Path = Path("bladeloads.png")
) -> None:
    """Plot blade loads from a list of dictionaries for multiple operating points."""
    if not loads_list:
        return
    fig, axs = plot_grid(len(loads_list[0]), figsize=(25, 25))
    for idx, name in enumerate(loads_list[0].keys()):
        for i, load_dict in enumerate(loads_list):
            axs[idx].plot(r, load_dict[name], label=f"uinf={uinf_list[i]:.1f}")
        axs[idx].set_title(name)
        axs[idx].grid()
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=len(labels))
    fig.tight_layout()
    fig.savefig(of)
    logger.info(f"Saved {of}")


def plot_moments(
    r: np.ndarray, loads_list: List[Dict[str, np.ndarray]], uinf_list: List[float], moments_dict: Dict[str, np.ndarray], of: Path = Path("moments.png")
) -> None:
    """Plot sectional moment distributions and root moments."""
    fig, axs = plt.subplots(3, 1, figsize=(15, 20))
    # Compute sectional moments for each load
    sectional_flap_list = []
    sectional_edge_list = []
    for loads in loads_list:
        Np = loads['Np']
        Tp = loads['Tp']
        sectional_flap = np.array([np.trapz(Np[i:] * (r[i:] - r[i]), r[i:]) for i in range(len(r))])
        sectional_edge = np.array([np.trapz(Tp[i:] * (r[i:] - r[i]), r[i:]) for i in range(len(r))])
        sectional_flap_list.append(sectional_flap)
        sectional_edge_list.append(sectional_edge)
    # Flapwise sectional distribution
    for i, sec in enumerate(sectional_flap_list):
        axs[0].plot(r, sec, label=f"uinf={uinf_list[i]:.1f}")
    axs[0].set_title('Flapwise Sectional Moment Distribution')
    axs[0].set_ylabel('Sectional Moment (Nm)')
    axs[0].legend()
    axs[0].grid()
    # Edgewise sectional distribution
    for i, sec in enumerate(sectional_edge_list):
        axs[1].plot(r, sec, label=f"uinf={uinf_list[i]:.1f}")
    axs[1].set_title('Edgewise Sectional Moment Distribution')
    axs[1].set_ylabel('Sectional Moment (Nm)')
    axs[1].legend()
    axs[1].grid()
    # Root moments
    axs[2].plot(uinf_list, moments_dict['flapwise'], label='Flapwise Moment')
    axs[2].plot(uinf_list, moments_dict['edgewise'], label='Edgewise Moment')
    axs[2].plot(uinf_list, moments_dict['combined_rms'], label='Combined RMS Moment')
    axs[2].set_title('Root Moments')
    axs[2].set_ylabel('Moment (Nm)')
    axs[2].set_xlabel('uinf [m/s]')
    axs[2].legend()
    axs[2].grid()
    fig.tight_layout()
    fig.savefig(of)
    logger.info(f"saved {of}")


def rotorplot(
    op: Dict[str, Any],
    uinf: np.ndarray,
    labels: List[str] = ["P", "CP", "T", "Mb"],
    Uinf_low: Optional[float] = None,
    Uinf_high: Optional[float] = None,
    Uinf_switch: Optional[float] = None,
    of: Path = Path("__temp.png"),
) -> None:
    """Plot rotor performance data against wind speeds."""
    lab = [i for i in labels if i in op]
    fig, axs = plot_grid(len(lab), figsize=(15, 15))
    for n, i in enumerate(lab):
        axs[n].plot(uinf, op[i], label=f"{i} max={np.array(op[i]).max():.2f}", marker='o', alpha=0.5)
        axs[n].legend()
        axs[n].grid()
        if i == "P":
            axs[n].set_ylabel("P (W)")
        elif i == "CP":
            axs[n].set_ylabel("CP")
        elif i == "T":
            axs[n].set_ylabel("T (N)")
        elif i == "Mb":
            axs[n].set_ylabel("Mb (Nm)")
        elif i == "omega":
            axs[n].set_ylabel("Omega (RPM)")
        elif i == "pitch":
            axs[n].set_ylabel("Pitch (deg)")
        elif i == "tsr":
            axs[n].set_ylabel("TSR")
        elif i == "tip_speed":
            axs[n].set_ylabel("Tip Speed (m/s)")
        axs[n].set_xlabel("uinf [m/s]")
    # Add regime backgrounds
    if Uinf_low is not None and Uinf_high is not None and Uinf_switch is not None:
        for ax in axs[:len(lab)]:
            if Uinf_low > uinf.min():
                ax.axvspan(0, Uinf_low, alpha=0.25, color="lightblue", label="Min Speed")
            ax.axvspan(
                max(0, Uinf_low), Uinf_high, alpha=0.25, color="lightgreen", label="Opt Speed"
            )
            if Uinf_switch > Uinf_high:
                ax.axvspan(
                    Uinf_high, Uinf_switch, alpha=0.25, color="orange", label="Max Speed"
                )
                ax.axvspan(
                    Uinf_switch,
                    uinf.max(),
                    alpha=0.25,
                    color="lightcoral",
                    label="Max Power",
                )
            else:
                ax.axvspan(
                    Uinf_high,
                    uinf.max(),
                    alpha=0.25,
                    color="lightcoral",
                    label="Max Speed/Max Power",
                )
    fig.tight_layout()
    fig.savefig(of)
    logger.info(f"saved {of}")
