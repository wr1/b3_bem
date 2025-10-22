import numpy as np
from unittest.mock import Mock, patch
from b3_bem.core.optimizer import ControlOptimize
from ccblade.ccblade import CCBlade
from pathlib import Path


def test_control_optimize():
    """Test ControlOptimize class initialization and a simple optimize method."""
    # Mock rotor
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = ({"P": np.array([1e7]), "T": np.array([1e5]), "CT": np.array([0.5]), "CP": np.array([0.4]), "Mb": np.array([1e6])}, None)
    rotor.r = np.linspace(0, 60, 50)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([6]), Path("/tmp"))
    # Test optimize_mid
    optimizer.Omega_opt = 5.0
    optimizer.pitch_opt = 0.0
    result = optimizer.optimize_mid(6.0)
    assert len(result) == 8
    assert isinstance(result[0], (float, np.floating))


def test_optimize_all():
    """Test full optimize_all in serial mode."""
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = ({"P": np.array([1e7]), "T": np.array([1e5]), "CT": np.array([0.5]), "CP": np.array([0.4]), "Mb": np.array([1e6])}, None)
    rotor.r = np.linspace(0, 60, 50)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([5, 10]), Path("/tmp"), serial=True)
    results = optimizer.optimize_all()
    assert len(results) == 2
    assert results[0][0] == 5
    assert results[1][0] == 10
