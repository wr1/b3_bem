from pathlib import Path
from unittest.mock import Mock, patch, ANY
from b3_bem.core.step import B3BemStep
from b3_bem.cli.yml_portable import Config


def test_b3bem_step():
    """Test B3BemStep execution."""
    config_obj = Config(workdir="temp", general={}, geometry={}, bem={})
    with patch('b3_bem.core.step.yaml_make_portable') as mock_yaml, \
         patch('b3_bem.core.step.B3BemRun') as mock_run, \
         patch.object(B3BemStep, 'load_config', return_value={'workdir': 'temp'}):
        mock_yaml.return_value = config_obj
        mock_run_instance = Mock()
        mock_run.return_value = mock_run_instance
        step = B3BemStep("config.yml", force=True)
        step._execute()
        mock_run.assert_called_once_with(config_obj.model_dump(), ANY)
        mock_run_instance.run.assert_called_once()
