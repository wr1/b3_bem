# Plot rotor performance functions.

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import logging
from typing import Dict, List, Optional, Any

from .polars import plot_grid

logger = logging.getLogger(__name__)


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
