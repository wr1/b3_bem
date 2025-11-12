import numpy as np
import tempfile
from pathlib import Path
from b3_bem.utils.utils import load_polar, interpolate_polars
from ccblade.ccblade import CCAirfoil


def test_load_polar():
    """Test loading a polar file."""
    polar_data = """-180 0.0 0.0 0.0
-170 0.1 0.01 0.001
0 0.5 0.05 0.005
180 0.0 0.0 0.0
EOT
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as f:
        f.write(polar_data)
        path = Path(f.name)
    alpha, cl, cd, cm = load_polar(path)
    assert len(alpha) == 79  # Interpolated
    assert len(cl) == 79
    path.unlink()


def test_interpolate_polars():
    """Test interpolating polars."""
    # Mock polars
    polar1 = (0.2, ([0, 10], [0, 0.5], [0, 0.05], [0, 0.005]))
    polar2 = (0.3, ([0, 10], [0, 0.6], [0, 0.06], [0, 0.006]))
    polars = [polar1, polar2]
    tnew = np.array([0.2, 0.25, 0.3])
    output = interpolate_polars(polars, tnew)
    assert len(output) == 3
    assert isinstance(output[0], CCAirfoil)
