#!/usr/bin/env python3
"""CLI for B3 BEM using treeparse."""

from pathlib import Path
from treeparse import cli, command, option
from ..core.step import B3BemStep
from ..plots.plotter import B3BemPlotter
import logging
from rich.logging import RichHandler

# Configure logging with Rich formatting, no timestamps
logging.basicConfig(
    level=logging.INFO, handlers=[RichHandler(show_time=False)], format="%(message)s"
)


# Treeparse CLI for b3_bem
def run_b3bem_callback(yml: Path, force: bool = False, plot: bool = False):
    """Callback for running the B3 BEM step."""
    step = B3BemStep(str(yml), force=force)
    step.run()
    if plot:
        results_path = Path(yml).parent / step.config["workdir"] / "results.json"
        plotter = B3BemPlotter(results_path)
        plotter.plot_all(Path(yml).parent / step.config["workdir"])
        logging.info("Plots generated.")


def plot_b3bem_callback(results: Path, output_dir: Path = Path("."), run: str = None):
    """Callback for plotting B3 BEM results."""
    plotter = B3BemPlotter(results, run_name=run)
    plotter.plot_all(output_dir)


b3bem_cli = cli(
    name="b3-bem",
    help="Run B3 BEM analysis",
    line_connect=True,
    show_types=True,
    show_defaults=True,
)

b3bem_cli.commands.append(
    command(
        name="run",
        help="Run B3 BEM analysis",
        callback=run_b3bem_callback,
        arguments=[],
        options=[
            option(
                flags=["--yml", "-y"],
                arg_type=Path,
                required=True,
                help="Path to YAML config file",
            ),
            option(
                flags=["--force", "-f"],
                arg_type=bool,
                default=False,
                help="Force run despite statesman",
            ),
            option(
                flags=["--plot", "-p"],
                arg_type=bool,
                default=False,
                help="Generate plots after run",
            ),
        ],
    )
)

b3bem_cli.commands.append(
    command(
        name="plot",
        help="Plot B3 BEM results",
        callback=plot_b3bem_callback,
        arguments=[],
        options=[
            option(
                flags=["--results", "-r"],
                arg_type=Path,
                required=True,
                help="Path to results.json file",
            ),
            option(
                flags=["--output-dir", "-o"],
                arg_type=Path,
                default=Path("."),
                help="Output directory for plots",
            ),
            option(
                flags=["--run"],
                arg_type=str,
                default=None,
                help="Run name to plot (if multiple runs)",
            ),
        ],
    )
)


def main():
    """Main entry point for the CLI."""
    b3bem_cli.run()
