#!/usr/bin/env python3
"""Statesman step for running B3 BEM analysis."""

import logging
from pathlib import Path
from .runner import B3BemRun
from ..cli.yml_portable import yaml_make_portable
from statesman.core.base import Statesman

logger = logging.getLogger(__name__)


class B3BemStep(Statesman):
    """Statesman step for running B3 BEM analysis."""

    dependent_sections = ["general", "planform", "bem"]
    output_files = [
        "results.json",
    ]
    workdir_key = "workdir"

    def __init__(self, config_path, force=False):
        super().__init__(config_path)
        self.force = force

    def run(self):
        if self.force:
            self._execute()
        else:
            super().run()

    def _execute(self):
        """Execute the B3 BEM analysis step."""
        # Load config using custom loader
        config_data = yaml_make_portable(Path(self.config_path))
        self.config = config_data.model_dump()

        # Set workdir relative to YAML file
        self.workdir = Path(self.config_path).parent / self.config["workdir"]
        self.workdir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        # Run B3 BEM analysis
        ccblade = B3BemRun(self.config, Path(self.config_path).parent)
        ccblade.run()
        logger.info(f"B3 BEM analysis completed and saved to {self.workdir}")
