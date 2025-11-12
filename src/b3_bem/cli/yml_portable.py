from pathlib import Path
from ruamel.yaml import YAML
from pydantic import BaseModel
from typing import Any, Dict


class Config(BaseModel):
    workdir: str = "temp"
    general: Dict[str, Any] = {}
    geometry: Dict[str, Any] = {}
    bem: Dict[str, Any] = {}


def yaml_make_portable(path: Path):
    yaml = YAML()
    with open(path) as f:
        data = yaml.load(f)
    config = Config(**data)
    return config


def save_yaml(path: Path, config):
    yaml = YAML()
    with open(path, "w") as f:
        yaml.dump(config.model_dump(), f)
