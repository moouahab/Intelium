from tools.metrics import RunMetrics, record_run
from pathlib import Path
import json


def test_record_run_updates_counters(tmp_path):
    health_path = tmp_path / "health.json"
    record_run(health_path, RunMetrics(status="ok", started_at=0.0, duration_seconds=1.0))
    record_run(health_path, RunMetrics(status="error", started_at=1.0, duration_seconds=2.0, error="boom"))

    data = json.loads(health_path.read_text())
    assert data["counters"]["total"] == 2
    assert data["counters"]["success"] == 1
    assert data["counters"]["failure"] == 1
    assert data["last_run"]["status"] == "error"
