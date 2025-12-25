from typing import List
from pathlib import Path
from tools.http.url_utils import resolve_normalizer
from tools.config_utils import to_bool


def validate_auth(auth_conf: dict) -> List[str]:
    errors = []
    if not auth_conf:
        return errors
    hosts = auth_conf.get("hosts")
    if hosts is not None and not isinstance(hosts, dict):
        errors.append("authentication.hosts doit être un dictionnaire.")
    for host, headers in (hosts or {}).items():
        if not isinstance(headers, dict):
            errors.append(f"authentication.hosts.{host} doit être un dictionnaire de headers.")
    return errors


def validate_crawler(crawler_conf: dict) -> List[str]:
    errors = []
    if not isinstance(crawler_conf, dict):
        errors.append("crawler doit être un dictionnaire.")
        return errors
    max_concurrent = crawler_conf.get("max_concurrent", 1)
    try:
        int(max_concurrent)
    except (TypeError, ValueError):
        errors.append("crawler.max_concurrent doit être un entier.")
    normalizer = crawler_conf.get("url_normalizer", "strip")
    try:
        resolve_normalizer(normalizer)
    except Exception:
        errors.append("crawler.url_normalizer doit être parmi: strip, lower, strip-lower.")
    # stockage base_dir
    save_conf = crawler_conf.get("save")
    if isinstance(save_conf, dict):
        base_dir = save_conf.get("base_dir")
        if base_dir and not Path(base_dir).exists():
            errors.append(f"crawler.save.base_dir introuvable: {base_dir}")
    return errors


def validate_output(output_conf: dict) -> List[str]:
    errors = []
    if not isinstance(output_conf, dict):
        return ["output doit être un dictionnaire."]
    fmt = output_conf.get("format", "markdown").lower()
    if fmt not in {"markdown", "json"}:
        errors.append("output.format doit être 'markdown' ou 'json'.")
    ai_conf = output_conf.get("ai_report", {})
    if ai_conf and not isinstance(ai_conf, dict):
        errors.append("output.ai_report doit être un dictionnaire.")
        return errors
    if ai_conf.get("enabled", False):
        cmd = ai_conf.get("command", "")
        if not cmd:
            # on accepte l'auto-détection mais on signale si rien n'est détecté côté run
            pass
        prompt_path = ai_conf.get("prompt_path")
        if prompt_path:
            if not Path(prompt_path).exists():
                errors.append(f"output.ai_report.prompt_path introuvable: {prompt_path}")
    return errors
