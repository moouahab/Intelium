from __future__ import annotations

import logging
from typing import Any, Iterable, Set
from urllib.parse import urlparse

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


def _extract_source_hosts(config: dict) -> Set[str]:
    sources = config.get("sources", [])
    if isinstance(sources, dict):
        sources = sources.get("sources", [])
    if not isinstance(sources, list):
        return set()
    hosts: Set[str] = set()
    for src in sources:
        if not isinstance(src, dict):
            continue
        url = src.get("url")
        if not url or not isinstance(url, str):
            continue
        host = urlparse(url).hostname
        if host:
            hosts.add(host.lower())
    return hosts


def _host_matches(auth_host: str, source_hosts: Set[str]) -> bool:
    if not source_hosts:
        return True
    auth_host = auth_host.lower()
    if auth_host in source_hosts:
        return True
    for src_host in source_hosts:
        if src_host.endswith(f".{auth_host}"):
            return True
    return False


def _is_invalid_env_value(key: str, value: str) -> bool:
    raw = str(value).strip()
    if not raw:
        return True
    if key == "SLACK_WEBHOOK_URL":
        parsed = urlparse(raw)
        return parsed.scheme not in {"http", "https"} or not parsed.netloc
    if key in {"ALERT_EMAIL_TO", "ALERT_EMAIL_FROM"}:
        return "@" not in raw or raw.startswith("@") or raw.endswith("@")
    if key == "SMTP_HOST":
        return not raw
    if key == "SMTP_PORT":
        try:
            port = int(raw)
            return port <= 0
        except Exception:
            return True
    return False


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
        if auth_conf:
            # Toujours inclure les headers globaux (pas liés à un host spécifique).
            required.update(_find_env_placeholders(auth_conf.get("headers", {})))
            hosts = auth_conf.get("hosts", {}) or {}
            source_hosts = _extract_source_hosts(config)
            scoped_hosts = {host: conf for host, conf in hosts.items() if _host_matches(host, source_hosts)}
            required.update(_find_env_placeholders(scoped_hosts))

    return required


def check_env_requirements(config: dict, auth_conf: dict | None, logger: logging.Logger | None = None) -> bool:
    ops = config.get("ops", {}) or {}
    strict = bool(ops.get("strict_env", False))
    required = collect_required_env(config, auth_conf=auth_conf)
    if not required:
        return True

    missing = []
    invalid = []
    for key in sorted(required):
        val = get_secret(key)
        if not val:
            missing.append(key)
            continue
        if _is_invalid_env_value(key, val):
            invalid.append(key)

    if not missing and not invalid:
        return True

    log = logger or logging.getLogger("preflight")
    if missing:
        msg = "Variables d'environnement manquantes: " + ", ".join(missing)
        if strict:
            log.error(msg)
        else:
            log.warning(msg)
    if invalid:
        msg = "Variables d'environnement invalides: " + ", ".join(invalid)
        if strict:
            log.error(msg)
        else:
            log.warning(msg)
    return not strict
