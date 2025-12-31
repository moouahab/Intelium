from pathlib import Path
from tools import metrics


def test_record_fetch_tracks_status_reason_and_bytes(tmp_path):
    path = tmp_path / "health.json"
    metrics.record_fetch(path, duration_seconds=1.0, status="downloaded", reason="ok", size_bytes=123)
    data = metrics._load_health(path)
    fetch = data["fetch"]
    assert fetch["total"] == 1
    assert fetch["success"] == 1
    assert fetch["bytes_total"] == 123
    assert fetch["reasons"]["ok"] == 1
    assert fetch["per_status"]["downloaded"] == 1
