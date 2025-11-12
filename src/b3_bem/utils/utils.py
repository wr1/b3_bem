# Utility functions for b3_bem.

from pathlib import Path
import numpy as np
from ccblade.ccblade import CCAirfoil
import os
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def load_polar(pname: Path) -> Tuple[List[float], np.ndarray, np.ndarray, np.ndarray]:
    """Load and interpolate a polar by name to a set alpha range."""
    logger.info(f"loading polar {pname}")
    if not os.path.isfile(pname):
        raise IOError(f"Polar {pname} not found")

    with open(pname, "r") as f:
        lines = f.readlines()

    read_start_index = next(
        i for i, line in enumerate(lines) if line.startswith("-180")
    )
    read_end_index = next((i for i, line in enumerate(lines) if "EOT" in line), None)

    lst = [
        [float(j) for j in line.split()]
        for line in lines[read_start_index:read_end_index]
    ]
    g = list(zip(*lst))
    alpha_new = (
        list(np.linspace(-180, -20, 25))
        + list(np.linspace(-19, 20, 29))
        + list(np.linspace(21, 180, 25))
    )
    cl = np.interp(alpha_new, g[0], g[1])
    cd = np.interp(alpha_new, g[0], g[2])
    cm = np.interp(alpha_new, g[0], g[3])
    return [alpha_new, cl, cd, cm]


def interpolate_polars(
    polars: List[tuple], tnew: np.ndarray, of: Optional[Path] = None
) -> List[CCAirfoil]:
    """Interpolate polars to new thickness values and return CCAirfoil objects."""
    indices = range(len(polars[0][1][0]))
    t = [polar[0] for polar in polars]
    data = np.array(
        [
            [
                np.interp(
                    np.flip(tnew),
                    np.flip(t),
                    np.flip([polar[1][i][idx] for polar in polars]),
                )
                for idx in indices
            ]
            for i in range(4)
        ]
    )
    output_polars = [
        CCAirfoil(
            Re=[1e6],
            alpha=data[0, :, i],
            cl=data[1, :, i],
            cd=data[2, :, i],
            cm=data[3, :, i],
        )
        for i in reversed(range(len(tnew)))
    ]
    if of:
        from b3_bem.plots import plot_polars, plot_interpolated_polars
        plot_polars(polars, of=of.with_name(of.stem + "_in" + of.suffix))
        plot_interpolated_polars(tnew, data, of=of)
    return output_polars
