import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse


ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _apply_env(value: Any) -> Any:
    """
    Remplace les tokens ${VAR} par la valeur d'environnement correspondante si présente.
    Supporte les str/dict/list récursivement, laisse intact si env manquant.
    """
    if isinstance(value, str):
        def repl(match):
            key = match.group(1)
            return os.getenv(key, match.group(0))
        return ENV_PATTERN.sub(repl, value)
    if isinstance(value, dict):
        return {k: _apply_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_apply_env(item) for item in value]
    return value


def load_auth(path: str | Path) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(Path(path).read_text())
    except FileNotFoundError:
        return {}
    except yaml.YAMLError:
        return {}
    auth_data = data.get("authentication", {}) if isinstance(data, dict) else {}
    return _apply_env(auth_data)


def build_headers(url: str, auth_conf: Dict[str, Any]) -> Dict[str, str]:
    """
    Fusionne les headers globaux et spécifiques au host (configurables dans auth.yaml).
    auth_conf peut contenir une clé 'headers' globale et une section 'hosts' avec des entrées par domaine.
    """
    if not auth_conf:
        return {}
    base = auth_conf.get("headers", {}) or {}

    host = urlparse(url).hostname or ""
    hosts_section = auth_conf.get("hosts", {})
    custom_host_headers = hosts_section.get(host, {}) if isinstance(hosts_section, dict) else {}

    merged = dict(base)
    merged.update(custom_host_headers)
    return {k: v for k, v in merged.items() if v}
