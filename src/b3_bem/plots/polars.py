# Plot polars functions.

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
import math
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


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
