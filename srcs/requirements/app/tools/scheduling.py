from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Optional

from tools.config.config_utils import to_bool, to_int


def parse_interval_seconds(value: Any, default: int = 3600) -> int:
    """
    Convertit un intervalle sous forme str ou int en secondes.
    Accepte "6h", "15m", "30s", "1d" ou un entier (secondes).
    """
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return default
    text = value.strip().lower()
    if text.endswith("ms"):
        num = to_int(text[:-2], default=None)
        return int(num / 1000) if num is not None else default
    if text.endswith("s"):
        num = to_int(text[:-1], default=None)
        return num if num is not None else default
    if text.endswith("m"):
        num = to_int(text[:-1], default=None)
        return num * 60 if num is not None else default
    if text.endswith("h"):
        num = to_int(text[:-1], default=None)
        return num * 3600 if num is not None else default
    if text.endswith("d"):
        num = to_int(text[:-1], default=None)
        return num * 86400 if num is not None else default
    return to_int(text, default=default) or default


@dataclass
class ScheduleConfig:
    interval_seconds: int
    retry_on_failure: bool
    max_retries: int
    backoff_factor: int
    start_time: Optional[str] = None
    timezone: Optional[str] = None


def load_schedule_config(raw: dict | None) -> ScheduleConfig:
    raw = raw or {}
    interval_seconds = parse_interval_seconds(raw.get("interval", "6h"), default=21600)
    return ScheduleConfig(
        interval_seconds=interval_seconds,
        retry_on_failure=to_bool(raw.get("retry_on_failure", True), default=True),
        max_retries=to_int(raw.get("max_retries", 3), default=3) or 3,
        backoff_factor=to_int(raw.get("backoff_factor", 2), default=2) or 2,
        start_time=raw.get("start_time"),
        timezone=raw.get("timezone"),
    )


def compute_initial_delay(start_time: Optional[str], now: Optional[dt.datetime] = None) -> int:
    """
    Retourne le délai (secondes) avant le premier run, en fonction de start_time HH:MM.
    Si start_time est passé, planifie pour le lendemain.
    """
    if not start_time:
        return 0
    now = now or dt.datetime.now()
    try:
        hour, minute = [int(x) for x in start_time.split(":")]
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except Exception:
        return 0
    if target <= now:
        target = target + dt.timedelta(days=1)
    return int((target - now).total_seconds())
