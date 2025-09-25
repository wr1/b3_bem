# B3 BEM analysis functions.

from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import fmin
from ccblade.ccblade import CCAirfoil, CCBlade
import os
import logging
from typing import List, Tuple, Dict, Optional, Any
from rich.live import Live
from rich.spinner import Spinner
from contextlib import redirect_stdout, redirect_stderr
import math

from ..plots.plots import (
    plot_interpolated_polars,
    plot_polars,
    plot_grid,
    plot_bladeloads,
    plot_moments,
    rotorplot,
)

from ..utils.utils import load_polar, interpolate_polars, tsr2omega, omega2tsr, find_closest_x
from .optimizer import RotorOptimizer, ControlOptimize
from .runner import B3BemRun

logger = logging.getLogger(__name__)
