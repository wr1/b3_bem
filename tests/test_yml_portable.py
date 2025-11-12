import tempfile
from pathlib import Path
from b3_bem.cli.yml_portable import yaml_make_portable, Config, save_yaml


def test_config():
    """Test Config model."""
    config = Config(workdir="test", general={}, geometry={}, bem={})
    assert config.workdir == "test"
    assert config.general == {}
    assert config.geometry == {}
    assert config.bem == {}


def test_yaml_make_portable():
    """Test loading YAML config."""
    data = """workdir: temp
general: {}
geometry: {}
bem: {}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(data)
        path = Path(f.name)
    config = yaml_make_portable(path)
    assert config.workdir == "temp"
    path.unlink()


def test_save_yaml():
    """Test saving YAML config."""
    config = Config(workdir="test", general={}, geometry={}, bem={})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        path = Path(f.name)
    save_yaml(path, config)
    # Reload and check
    reloaded = yaml_make_portable(path)
    assert reloaded.workdir == "test"
    path.unlink()
