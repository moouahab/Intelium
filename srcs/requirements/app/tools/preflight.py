from __future__ import annotations

import logging
from typing import Any, Iterable, Set

from tools.auth import ENV_PATTERN
from tools.secrets import get_secret


def _find_env_placeholders(value: Any) -> Set[str]:
    found: Set[str] = set()
    if isinstance(value, str):
        for match in ENV_PATTERN.finditer(value):
            found.add(match.group(1))
    elif isinstance(value, dict):
        for item in value.values():
            found.update(_find_env_placeholders(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_find_env_placeholders(item))
    return found


def _uses_mistral(ai_conf: dict) -> bool:
    command = " ".join(
        [
            str(ai_conf.get("command") or ""),
            str(ai_conf.get("langgraph_llm_command") or ""),
            str(ai_conf.get("mode") or ""),
        ]
    ).lower()
    if "mistral" in command:
        return True
    provider = (ai_conf.get("provider") or "").lower()
    return provider == "mistral"


def collect_required_env(config: dict, auth_conf: dict | None = None) -> Set[str]:
    ops = config.get("ops", {}) or {}
    required: Set[str] = set(ops.get("required_env", []) or [])

    cache_conf = config.get("cache", {}) or {}
    if (cache_conf.get("backend") or "").lower() == "mongo":
        required.add("MONGO_URI")

    output_conf = config.get("output", {}) or {}
    ai_conf = output_conf.get("ai_report", {}) or {}
    if ai_conf.get("enabled") and _uses_mistral(ai_conf):
        required.add("MISTRAL_API_KEY")

    if ops.get("require_alerting_env", False):
        required.update(
            {
                "SLACK_WEBHOOK_URL",
                "ALERT_EMAIL_TO",
                "ALERT_EMAIL_FROM",
                "SMTP_HOST",
                "SMTP_PORT",
            }
        )

    if ops.get("require_auth_env", True):
        required.update(_find_env_placeholders(auth_conf or {}))

    return required


def check_env_requirements(config: dict, auth_conf: dict | None, logger: logging.Logger | None = None) -> bool:
    ops = config.get("ops", {}) or {}
    strict = bool(ops.get("strict_env", False))
    required = collect_required_env(config, auth_conf=auth_conf)
    if not required:
        return True

    missing = [key for key in sorted(required) if not get_secret(key)]
    if not missing:
        return True

    log = logger or logging.getLogger("preflight")
    msg = "Variables d'environnement manquantes: " + ", ".join(missing)
    if strict:
        log.error(msg)
        return False
    log.warning(msg)
    return True
