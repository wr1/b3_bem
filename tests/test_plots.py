import numpy as np
import json
from unittest.mock import patch, Mock, mock_open
from b3_bem.plots.planform import plot_planform
from b3_bem.plots.polars import plot_interpolated_polars, plot_polars
from b3_bem.plots.bladeloads import plot_bladeloads, plot_moments
from b3_bem.plots.rotor import rotorplot
from b3_bem.plots.plotter import B3BemPlotter
from pathlib import Path


def test_plot_planform():
    """Test plot_planform."""
    with patch('b3_bem.plots.planform.plt.subplots') as mock_subplots, \
         patch('b3_bem.plots.planform.plt.savefig'), \
         patch('b3_bem.plots.planform.plt.close'):
        mock_fig = Mock()
        mock_axs = np.array([[Mock() for _ in range(2)] for _ in range(2)])
        mock_subplots.return_value = (mock_fig, mock_axs)
        plot_planform(np.array([0, 1]), np.array([1, 0.5]), np.array([0, 10]), np.array([0.2, 0.1]))
        mock_subplots.assert_called_once()


def test_plot_interpolated_polars():
    """Test plot_interpolated_polars."""
    data = np.random.rand(4, 79, 3)
    t = [0.2, 0.25, 0.3]
    with patch('b3_bem.plots.polars.plt.subplots') as mock_subplots, \
         patch('b3_bem.plots.polars.plt.savefig'), \
         patch('b3_bem.plots.polars.plt.tight_layout'):
        mock_fig = Mock()
        mock_ax = [Mock() for _ in range(3)]
        mock_subplots.return_value = (mock_fig, mock_ax)
        plot_interpolated_polars(t, data)
        mock_subplots.assert_called_once()


def test_plot_polars():
    """Test plot_polars."""
    polars = [(0.2, ([0, 10], [0, 0.5], [0, 0.05], [0, 0.005]))]
    with patch('b3_bem.plots.polars.plt.subplots') as mock_subplots, \
         patch('b3_bem.plots.polars.plt.savefig'), \
         patch('b3_bem.plots.polars.plt.tight_layout'):
        mock_fig = Mock()
        mock_ax = [Mock() for _ in range(3)]
        mock_subplots.return_value = (mock_fig, mock_ax)
        plot_polars(polars)
        mock_subplots.assert_called_once()


def test_plot_bladeloads():
    """Test plot_bladeloads."""
    r = np.linspace(0, 60, 50)
    loads_list = [{'Np': np.ones(50), 'Tp': np.ones(50)}]
    uinf_list = [6.0]
    with patch('b3_bem.plots.bladeloads.plot_grid') as mock_plot_grid, \
         patch('b3_bem.plots.bladeloads.plt.savefig'), \
         patch('b3_bem.plots.bladeloads.plt.tight_layout'):
        mock_fig = Mock()
        mock_axs = [Mock() for _ in range(2)]
        mock_plot_grid.return_value = (mock_fig, mock_axs)
        # Configure mock axes to return a tuple for get_legend_handles_labels
        for ax in mock_axs:
            ax.get_legend_handles_labels.return_value = ([], [])
        plot_bladeloads(r, loads_list, uinf_list)
        mock_plot_grid.assert_called_once()


def test_plot_moments():
    """Test plot_moments."""
    r = np.linspace(0, 60, 50)
    loads_list = [{'Np': np.ones(50), 'Tp': np.ones(50)}]
    uinf_list = [6.0]
    moments_dict = {'flapwise': np.array([1e6]), 'edgewise': np.array([5e5]), 'combined_rms': np.array([1.118e6])}
    with patch('b3_bem.plots.bladeloads.plt.subplots') as mock_subplots, \
         patch('b3_bem.plots.bladeloads.plt.savefig'), \
         patch('b3_bem.plots.bladeloads.plt.tight_layout'):
        mock_fig = Mock()
        mock_axs = [Mock() for _ in range(3)]
        mock_subplots.return_value = (mock_fig, mock_axs)
        plot_moments(r, loads_list, uinf_list, moments_dict)
        mock_subplots.assert_called_once()


def test_rotorplot():
    """Test rotorplot."""
    op = {'P': [1e6, 2e6], 'CP': [0.4, 0.45]}
    uinf = np.array([6, 10])
    with patch('b3_bem.plots.rotor.plot_grid') as mock_plot_grid, \
         patch('b3_bem.plots.rotor.plt.savefig'), \
         patch('b3_bem.plots.rotor.plt.tight_layout'):
        mock_fig = Mock()
        mock_axs = [Mock() for _ in range(2)]
        mock_plot_grid.return_value = (mock_fig, mock_axs)
        rotorplot(op, uinf)
        mock_plot_grid.assert_called_once()


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
