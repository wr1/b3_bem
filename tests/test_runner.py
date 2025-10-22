import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from b3_bem.core.runner import B3BemRun


def test_b3bem_run_init():
    """Test B3BemRun initialization."""
    config = {
        "workdir": "temp",
        "bem": {"uinf": [5, 10], "B": 3, "rho": 1.225, "mu": 1.8e-5, "precone": 0, "tilt": 0, "yaw": 0, "shearExp": 0, "hubHt": 80, "max_tipspeed": 80, "rated_power": 1e6, "polars": []},
        "geometry": {"planform": {"chord": [[0, 1], [1, 0.5]], "twist": [[0, 0], [1, 10]], "thickness": [[0, 0.2], [1, 0.1]], "z": [[0, 0], [1, 100]]}}
    }
    yml_dir = Path("/tmp")
    with patch('b3_bem.core.runner.CCBlade') as mock_ccblade, \
         patch('b3_bem.core.runner.plot_planform'), \
         patch('b3_bem.core.runner.interpolate_polars') as mock_interp, \
         patch('b3_bem.core.runner.load_polar'):
        mock_interp.return_value = Mock()
        runner = B3BemRun(config, yml_dir)
        assert runner.config == config
        assert 'r' in runner.planform_data
