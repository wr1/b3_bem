import numpy as np
import json
from unittest.mock import patch, Mock, mock_open
from b3_bem.plots.plots import plot_planform
from b3_bem.plots.plotter import B3BemPlotter
from pathlib import Path


def test_plot_planform():
    """Test plot_planform."""
    with patch('b3_bem.plots.plots.plt.subplots') as mock_subplots, \
         patch('b3_bem.plots.plots.plt.savefig'), \
         patch('b3_bem.plots.plots.plt.close'):
        mock_fig = Mock()
        mock_axs = np.array([[Mock() for _ in range(2)] for _ in range(2)])
        mock_subplots.return_value = (mock_fig, mock_axs)
        plot_planform(np.array([0, 1]), np.array([1, 0.5]), np.array([0, 10]), np.array([0.2, 0.1]))
        mock_subplots.assert_called_once()


def test_plotter():
    """Test B3BemPlotter."""
    data = {
        "planform": {"r": [0, 1], "chord": [1, 0.5], "twist": [0, 10], "thickness": [0.2, 0.1]},
        "performance": {"uinf": [5, 10], "P": [100, 200]},
        "blade_loads": {"r": [0, 1], "loads_list": [{"Np": [1, 2], "Tp": [0.1, 0.2]}], "uinf_list": [5], "flapwise_moments": [10], "edgewise_moments": [5], "combined_rms": [11.2]},
        "metadata": {"Uinf_low": 4, "Uinf_high": 8, "Uinf_switch": 12}
    }
    with patch('b3_bem.plots.plotter.open', mock_open(read_data=json.dumps(data))), \
         patch('b3_bem.plots.plotter.plot_planform'), \
         patch('b3_bem.plots.plotter.rotorplot'), \
         patch('b3_bem.plots.plotter.plot_bladeloads'), \
         patch('b3_bem.plots.plotter.plot_moments'):
        plotter = B3BemPlotter(Path("dummy.json"))
        plotter.plot_all()
        assert "planform" in plotter.data
