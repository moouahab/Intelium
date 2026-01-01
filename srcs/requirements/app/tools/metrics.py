from __future__ import annotations

import json
import time
import threading
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


_METRICS_LOCK = threading.Lock()


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


def _write_health(metrics_path: Path, payload: dict) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2))
    tmp_path.replace(metrics_path)


def record_run(metrics_path: str | Path, metrics: RunMetrics) -> None:
    """
    Enrichit health.json avec le dernier run + compteurs succès/échec.
    """
    metrics_path = Path(metrics_path)
    with _METRICS_LOCK:
        payload = _load_health(metrics_path)
        payload.setdefault("counters", {"total": 0, "success": 0, "failure": 0})
        payload["last_run"] = metrics.to_dict()
        payload["last_run_at"] = metrics.started_at
        payload["counters"]["total"] += 1
        if metrics.status == "ok":
            payload["counters"]["success"] += 1
        else:
            payload["counters"]["failure"] += 1
        _write_health(metrics_path, payload)


def record_fetch(
    metrics_path: str | Path,
    duration_seconds: float,
    status: str,
    reason: Optional[str] = None,
    size_bytes: Optional[int] = None,
    source_name: Optional[str] = None,
    url: Optional[str] = None,
) -> None:
    """
    Enregistre un fetch individuel (succès/erreur) avec comptage et durée cumulée.
    """
    metrics_path = Path(metrics_path)
    with _METRICS_LOCK:
        payload = _load_health(metrics_path)
        fetch = payload.setdefault(
            "fetch",
            {"total": 0, "success": 0, "failure": 0, "duration_sum": 0.0, "reasons": {}, "per_status": {}, "bytes_total": 0},
        )
        fetch.setdefault("bytes_total", 0)
        reasons = fetch.setdefault("reasons", {})
        per_status = fetch.setdefault("per_status", {})
        fetch["bytes_total"] += int(size_bytes or 0)
        fetch["total"] += 1
        fetch["duration_sum"] += float(duration_seconds)
        if status == "downloaded":
            fetch["success"] += 1
        else:
            fetch["failure"] += 1
        if reason:
            reasons[reason] = reasons.get(reason, 0) + 1
        per_status[status] = per_status.get(status, 0) + 1
        fetch["reasons"] = reasons
        fetch["per_status"] = per_status
        if status != "downloaded":
            recent = fetch.setdefault("recent_errors", [])
            recent.append(
                {
                    "ts": time.time(),
                    "source": source_name,
                    "url": url,
                    "status": status,
                    "reason": reason,
                }
            )
            if len(recent) > 50:
                fetch["recent_errors"] = recent[-50:]
        payload["fetch"] = fetch
        _write_health(metrics_path, payload)


def time_block():
    start = time.time()
    yield lambda: time.time() - start
