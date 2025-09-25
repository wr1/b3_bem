# Airfoil and geometry loading utilities.

import contextlib
import logging

logger = logging.getLogger(__name__)


def load(fl, normalise=False):
    """
    Load airfoil coordinates from file.

    args:
        fl (str or Path): filename

    kwargs:
        normalise (bool): flag determining whether the airfoil is normalised to
        unit length

    returns:
        List of [x, y] coordinate pairs
    """
    d = []
    logger.info(f"loading airfoil {fl}")
    for i in open(fl, "r"):
        with contextlib.suppress(Exception):
            xy = [float(j) for j in i.split()]
            if len(xy) in {2, 3}:
                d.append(xy)
    x, y = list(zip(*d))
    if normalise:
        mx = min(x)
        dx = max(x) - min(x)
        logger.info("normalise factor %f" % dx)
        x = [(i - mx) / dx for i in x]
        y = [i / dx for i in y]

    return [[float(x_), float(y_)] for x_, y_ in zip(x, y)]
