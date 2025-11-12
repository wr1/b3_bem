from unittest.mock import patch, Mock
from b3_bem.cli.cli import b3bem_cli, run_b3bem_callback, plot_b3bem_callback
from pathlib import Path


def test_cli():
    """Test CLI structure."""
    assert len(b3bem_cli.commands) == 2
    assert b3bem_cli.commands[0].name == "run"
    assert b3bem_cli.commands[1].name == "plot"


def test_run_b3bem_callback():
    """Test run_b3bem_callback."""
    with (
        patch("b3_bem.cli.cli.B3BemStep") as mock_step,
        patch("b3_bem.cli.cli.B3BemPlotter") as mock_plotter,
        patch("b3_bem.cli.cli.logging") as mock_logging,
    ):
        mock_step_instance = Mock()
        mock_step_instance.config = {"workdir": "temp"}
        mock_step.return_value = mock_step_instance
        mock_plotter_instance = Mock()
        mock_plotter.return_value = mock_plotter_instance
        run_b3bem_callback(Path("test.yml"), force=True, plot=True)
        mock_step.assert_called_once_with(str(Path("test.yml")), force=True)
        mock_step_instance.run.assert_called_once()
        mock_plotter.assert_called_once_with(Path("temp") / "results.json")
        mock_plotter_instance.plot_all.assert_called_once_with(Path("temp"))
        mock_logging.info.assert_called_once_with("Plots generated.")


def test_plot_b3bem_callback():
    """Test plot_b3bem_callback."""
    with patch("b3_bem.cli.cli.B3BemPlotter") as mock_plotter:
        mock_plotter_instance = Mock()
        mock_plotter.return_value = mock_plotter_instance
        plot_b3bem_callback(Path("results.json"), Path("output"))
        mock_plotter.assert_called_once_with(Path("results.json"), run_name=None)
        mock_plotter_instance.plot_all.assert_called_once_with(Path("output"))
