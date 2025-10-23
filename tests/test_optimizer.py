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


def test_optimize_low():
    """Test optimize_low method."""
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = ({"P": np.array([1e7]), "T": np.array([1e5]), "CT": np.array([0.5]), "CP": np.array([0.4]), "Mb": np.array([1e6])}, None)
    rotor.r = np.linspace(0, 60, 50)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([3]), Path("/tmp"))
    optimizer.Uinf_low = 5
    optimizer.pitch_opt = 0.0
    result = optimizer.optimize_low(3.0)
    assert len(result) == 8


def test_optimize_upper():
    """Test optimize_upper method."""
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = ({"P": np.array([1e7]), "T": np.array([1e5]), "CT": np.array([0.5]), "CP": np.array([0.4]), "Mb": np.array([1e6])}, None)
    rotor.r = np.linspace(0, 60, 50)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([10]), Path("/tmp"))
    optimizer.Uinf_high = 8
    optimizer.pitch_opt = 0.0
    result = optimizer.optimize_upper(10.0)
    assert len(result) == 8


def test_optimize_high():
    """Test optimize_high method."""
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = ({"P": np.array([1e7]), "T": np.array([1e5]), "CT": np.array([0.5]), "CP": np.array([0.4]), "Mb": np.array([1e6])}, None)
    rotor.r = np.linspace(0, 60, 50)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([15]), Path("/tmp"))
    optimizer.Uinf_high = 8
    optimizer.pitch_opt = 0.0
    result = optimizer.optimize_high(15.0)
    assert len(result) == 8


def test_compute_bladeloads():
    """Test compute_bladeloads method."""
    rotor = Mock(spec=CCBlade)
    rotor.r = np.linspace(0, 60, 50)
    loads = {'Np': np.ones(50), 'Tp': np.ones(50)}
    rotor.distributedAeroLoads.return_value = (loads, None)
    optimizer = ControlOptimize(rotor, 95, 60, 1e7, np.array([6]), Path("/tmp"))
    results = [(6.0, 'mid', 5.0, 0.0, 1e6, 1e5, 0.5, 0.4, 1e6, 10)]
    blade_data = optimizer.compute_bladeloads(results)
    assert 'r' in blade_data
    assert 'loads_list' in blade_data
    assert len(blade_data['loads_list']) == 1
    assert 'flapwise_moments' in blade_data
    assert 'edgewise_moments' in blade_data
    assert 'combined_rms' in blade_data


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
