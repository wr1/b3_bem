from unittest.mock import patch
from b3_bem.cli.cli import b3bem_cli


def test_cli():
    """Test CLI structure."""
    assert len(b3bem_cli.commands) == 2
    assert b3bem_cli.commands[0].name == "run"
    assert b3bem_cli.commands[1].name == "plot"
