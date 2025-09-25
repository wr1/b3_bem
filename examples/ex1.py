#!/usr/bin/env python3
"""Programmatic example of running B3 BEM analysis for a simple blade."""

from pathlib import Path
from b3_bem.core.step import B3BemStep

# Example config path (using the provided blade_test.yml)
config_path = Path(__file__).parent / ".." / "config" / "data" / "blade_test.yml"

# Create and run the step with force=True to bypass statesman checks
step = B3BemStep(str(config_path), force=True)
step.run()

print("B3 BEM analysis completed.")
