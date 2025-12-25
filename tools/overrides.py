from __future__ import annotations

from typing import Any, Dict, Optional


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "no", "n", ""}
    return bool(value)


def normalize_overrides(raw: Optional[dict]) -> dict:
    """
    Nettoie/normalise les overrides. Supporte :
    - max_bytes (int)
    - respect_robots (bool)
    - crawl_delay_seconds (int)
    - headers (dict de str)
    - user_agent (str)
    """
    if not isinstance(raw, dict):
        return {}
    overrides = dict(raw)
    max_bytes = _to_int(overrides.get("max_bytes"))
    if max_bytes is None:
        overrides.pop("max_bytes", None)
    else:
        overrides["max_bytes"] = max_bytes

    if "respect_robots" in overrides:
        overrides["respect_robots"] = _to_bool(overrides.get("respect_robots"))

    crawl_delay = _to_int(overrides.get("crawl_delay_seconds"))
    if crawl_delay is None:
        overrides.pop("crawl_delay_seconds", None)
    else:
        overrides["crawl_delay_seconds"] = crawl_delay

    headers = overrides.get("headers")
    if headers is None:
        overrides.pop("headers", None)
    elif not isinstance(headers, dict):
        overrides.pop("headers", None)

    user_agent = overrides.get("user_agent")
    if user_agent is None or not isinstance(user_agent, str) or not user_agent.strip():
        overrides.pop("user_agent", None)
    else:
        overrides["user_agent"] = user_agent.strip()

    return overrides


def merge_headers(base_headers: Dict[str, str], override_headers: Optional[Dict[str, str]] = None, user_agent: Optional[str] = None) -> Dict[str, str]:
    """
    Fusionne les headers en appliquant un User-Agent par défaut (si fourni) puis les overrides.
    Les valeurs falsy sont ignorées.
    """
    merged: Dict[str, str] = {}
    for k, v in (base_headers or {}).items():
        if v:
            merged[k] = v
    if user_agent:
        merged.setdefault("User-Agent", user_agent)
    for k, v in (override_headers or {}).items():
        if v:
            merged[k] = v
    return merged
