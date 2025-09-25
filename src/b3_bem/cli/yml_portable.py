from pathlib import Path
from ruamel.yaml import YAML
from pydantic import BaseModel
from typing import Any, Dict, List
from ..utils.loft_utils import load


class Aero(BaseModel):
    airfoils: Dict[float, List[List[float]]] = {}


class Config(BaseModel):
    workdir: str = "temp"
    general: Dict[str, Any] = {}
    geometry: Dict[str, Any] = {}
    airfoils: List[Dict[str, Any]] = []
    aero: Aero = Aero()
    bem: Dict[str, Any] = {}
    mesh: Dict[str, Any] = {}
    mesh2d: Dict[str, Any] = {}
    materials: str = ""
    laminates: str = ""
    loads: str = ""
    damage: Dict[str, Any] = {}


def load_airfoils(afs, yml_dir):
    airfoils = {}
    for item in afs:
        key = item['key']
        if 'file' in item:
            airfoils[key] = load(yml_dir / item['file'])
        else:
            airfoils[key] = item['xy']
    return airfoils


def yaml_make_portable(path: Path):
    yaml = YAML()
    with open(path) as f:
        data = yaml.load(f)
    yml_dir = path.parent
    if 'airfoils' in data:
        data['aero'] = {'airfoils': load_airfoils(data['airfoils'], yml_dir)}
    config = Config(**data)
    return config


def save_yaml(path: Path, config):
    yaml = YAML()
    with open(path, 'w') as f:
        yaml.dump(config.model_dump(), f)
