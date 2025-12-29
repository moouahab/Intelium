from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class RunMetrics:
    status: str
    started_at: float
    duration_seconds: float
    error: Optional[str] = None
    report_path: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def _load_health(metrics_path: Path) -> dict:
    if not metrics_path.exists():
        return {}
    try:
        data = json.loads(metrics_path.read_text() or "{}")
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def record_run(metrics_path: str | Path, metrics: RunMetrics) -> None:
    """
    Enrichit health.json avec le dernier run + compteurs succès/échec.
    """
    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_health(metrics_path)
    payload.setdefault("counters", {"total": 0, "success": 0, "failure": 0})
    payload["last_run"] = metrics.to_dict()
    payload["last_run_at"] = metrics.started_at
    payload["counters"]["total"] += 1
    if metrics.status == "ok":
        payload["counters"]["success"] += 1
    else:
        payload["counters"]["failure"] += 1
    metrics_path.write_text(json.dumps(payload, indent=2))


def record_fetch(metrics_path: str | Path, duration_seconds: float, status: str) -> None:
    """
    Enregistre un fetch individuel (succès/erreur) avec comptage et durée cumulée.
    """
    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_health(metrics_path)
    fetch = payload.setdefault("fetch", {"total": 0, "success": 0, "failure": 0, "duration_sum": 0.0})
    fetch["total"] += 1
    fetch["duration_sum"] += float(duration_seconds)
    if status == "downloaded":
        fetch["success"] += 1
    else:
        fetch["failure"] += 1
    payload["fetch"] = fetch
    metrics_path.write_text(json.dumps(payload, indent=2))


def time_block():
    start = time.time()
    yield lambda: time.time() - start
