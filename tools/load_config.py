import json
from pathlib import Path
from typing import Any
import yaml


def load_yaml_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config introuvable: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    if "include" in data and isinstance(data["include"], list):
        for inc in data["include"]:
            inc_path = path.parent / inc
            include_data = yaml.safe_load(inc_path.read_text()) or {}
            data = _deep_merge(data, include_data)
    return data


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def get_config_as_json_string(config: dict) -> str:
    return json.dumps(config, indent=2)


def load_keywords_from_config(config: dict, default_path: str | Path | None = None) -> dict:
    kw_path = config.get("keywords")
    if kw_path:
        try:
            return json.loads(Path(kw_path).read_text())
        except (OSError, json.JSONDecodeError):
            pass
    if default_path:
        try:
            return json.loads(Path(default_path).read_text())
        except (OSError, json.JSONDecodeError):
            pass
    return {}
