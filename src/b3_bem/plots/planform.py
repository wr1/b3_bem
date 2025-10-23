# Plot planform functions.

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def plot_planform(r, chord, twist, thickness, of: Path = Path("ccblade_planform.png"), control_points: Optional[Dict[str, tuple]] = None) -> None:
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
