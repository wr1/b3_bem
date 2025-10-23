# Plot blade loads and moments functions.

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import logging
from typing import List, Dict
from scipy.integrate import trapezoid

from .polars import plot_grid

logger = logging.getLogger(__name__)


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
        sectional_flap = np.array([trapezoid(Np[i:] * (r[i:] - r[i]), r[i:]) for i in range(len(r))])
        sectional_edge = np.array([trapezoid(Tp[i:] * (r[i:] - r[i]), r[i:]) for i in range(len(r))])
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
