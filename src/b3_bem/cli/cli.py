#!/usr/bin/env python3
"""CLI for B3 BEM using treeparse."""

from pathlib import Path
from treeparse import cli, command, option
from ..core.step import B3BemStep


# Treeparse CLI for b3_bem
def run_b3bem_callback(yml: Path, force: bool = False):
    """Callback for running the B3 BEM step."""
    step = B3BemStep(str(yml), force=force)
    step.run()


b3bem_cli = cli(
    name="b3-bem",
    help="Run B3 BEM analysis",
    line_connect=True,
    show_types=True,
    show_defaults=True,
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
    ],
)

b3bem_cli.commands.append(
    command(
        name="run",
        help="Run B3 BEM analysis",
        callback=run_b3bem_callback,
        arguments=[],
    )
)
