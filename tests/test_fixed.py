import numpy as np
from unittest.mock import Mock
from b3_bem.core.fixed import FixedRun
from ccblade.ccblade import CCBlade


def test_fixed_run():
    """Test FixedRun run method."""
    rotor = Mock(spec=CCBlade)
    rotor.evaluate.return_value = (
        {
            "P": np.array([1e7]),
            "T": np.array([1e5]),
            "CT": np.array([0.5]),
            "CP": np.array([0.4]),
            "Mb": np.array([1e6]),
        },
        None,
    )
    rotor.r = np.linspace(0, 60, 50)
    operation = [{"uinf": 6, "omega": 5, "pitch": 0}]
    fixed_run = FixedRun(rotor, operation, 60)
    results = fixed_run.run()
    assert len(results) == 1
    assert results[0][0] == 6  # uinf
    assert results[0][1] == "fixed"
    assert results[0][2] == 5  # omega
    assert results[0][3] == 0  # pitch
    assert results[0][4] == 1e7  # P
    assert results[0][5] == 1e5  # T
    assert results[0][6] == 0.5  # CT
    assert results[0][7] == 0.4  # CP
    assert results[0][8] == 1e6  # Mb
    assert results[0][9] == 1  # niter


def test_fixed_compute_bladeloads():
    """Test FixedRun compute_bladeloads method."""
    rotor = Mock(spec=CCBlade)
    rotor.r = np.linspace(0, 60, 50)
    rotor.distributedAeroLoads.return_value = (
        {
            "Np": np.ones(50),
            "Tp": np.ones(50),
        },
        None,
    )
    operation = [{"uinf": 6, "omega": 5, "pitch": 0}]
    fixed_run = FixedRun(rotor, operation, 60)
    results = [(6, "fixed", 5, 0, 1e7, 1e5, 0.5, 0.4, 1e6, 1)]
    blade_data = fixed_run.compute_bladeloads(results)
    assert "r" in blade_data
    assert "loads_list" in blade_data
    assert "uinf_list" in blade_data
    assert len(blade_data["flapwise_moments"]) == 1
    # Check values: Np=1, Tp=1, r=linspace(0,60,50)
    # moment_flap = trapezoid(Np * r, r) = trapezoid(r, r) = 1800
    assert blade_data["flapwise_moments"][0] == 1800.0
    assert blade_data["edgewise_moments"][0] == 1800.0
    assert blade_data["combined_rms"][0] == 1800.0 * np.sqrt(2)
