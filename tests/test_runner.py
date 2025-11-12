from pathlib import Path
from unittest.mock import Mock, patch
from b3_bem.core.runner import B3BemRun


def test_b3bem_run_init():
    """Test B3BemRun initialization."""
    config = {
        "workdir": "temp",
        "bem": {
            "uinf": [5, 10],
            "B": 3,
            "rho": 1.225,
            "mu": 1.8e-5,
            "precone": 0,
            "tilt": 0,
            "yaw": 0,
            "shearExp": 0,
            "hubHt": 80,
            "max_tipspeed": 80,
            "rated_power": 1e6,
            "polars": [],
        },
        "geometry": {
            "planform": {
                "chord": [[0, 1], [1, 0.5]],
                "twist": [[0, 0], [1, 10]],
                "thickness": [[0, 0.2], [1, 0.1]],
                "z": [[0, 0], [1, 100]],
            }
        },
    }
    yml_dir = Path("/tmp")
    with (
        patch("b3_bem.core.runner.CCBlade"),
        patch("b3_bem.core.runner.plot_planform"),
        patch("b3_bem.core.runner.interpolate_polars") as mock_interp,
        patch("b3_bem.core.runner.load_polar"),
    ):
        mock_interp.return_value = Mock()
        runner = B3BemRun(config, yml_dir)
        assert runner.config == config
        assert "r" in runner.planform_data


def test_b3bem_run_run():
    """Test B3BemRun run method."""
    config = {
        "workdir": "temp",
        "bem": {
            "uinf": [5, 10],
            "B": 3,
            "rho": 1.225,
            "mu": 1.8e-5,
            "precone": 0,
            "tilt": 0,
            "yaw": 0,
            "shearExp": 0,
            "hubHt": 80,
            "max_tipspeed": 80,
            "rated_power": 1e6,
            "polars": [],
        },
        "geometry": {
            "planform": {
                "chord": [[0, 1], [1, 0.5]],
                "twist": [[0, 0], [1, 10]],
                "thickness": [[0, 0.2], [1, 0.1]],
                "z": [[0, 0], [1, 100]],
            }
        },
    }
    yml_dir = Path("/tmp")
    with (
        patch("b3_bem.core.runner.CCBlade"),
        patch("b3_bem.core.runner.plot_planform"),
        patch("b3_bem.core.runner.interpolate_polars") as mock_interp,
        patch("b3_bem.core.runner.ControlOptimize") as mock_opt_class,
        patch("b3_bem.core.runner.json.dump") as mock_json_dump,
        patch("b3_bem.core.runner.pd.Timestamp.now") as mock_now,
    ):
        mock_interp.return_value = Mock()
        mock_opt_instance = Mock()
        mock_opt_instance.optimize_all.return_value = [
            (5, "low", 2, 0, 1e5, 1e4, 0.5, 0.4, 1e5, 1),
            (10, "mid", 5, 0, 1e6, 1e5, 0.5, 0.4, 1e6, 1),
        ]
        mock_opt_instance.compute_bladeloads.return_value = {
            "r": [0, 1],
            "loads_list": [],
            "uinf_list": [5, 10],
            "flapwise_moments": [1e4, 1e5],
            "edgewise_moments": [5e3, 5e4],
            "combined_rms": [1.118e4, 1.118e5],
        }
        mock_opt_instance.Uinf_low = 4
        mock_opt_instance.Uinf_high = 8
        mock_opt_instance.Uinf_switch = 12
        mock_opt_instance.rtip = 60
        mock_opt_class.return_value = mock_opt_instance
        mock_now.return_value = "2023-01-01"
        runner = B3BemRun(config, yml_dir)
        runner.run()
        mock_opt_instance.optimize_all.assert_called_once()
        mock_opt_instance.compute_bladeloads.assert_called_once()
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        data = args[0]
        assert "performance" in data
        assert "blade_loads" in data
        assert "metadata" in data
