from tools.observability import health_summary


def test_summary_includes_last_run_at():
    payload = {
        "fetch": {},
        "counters": {"total": 1, "success": 1, "failure": 0},
        "last_run": {"status": "ok", "duration_seconds": 1.2},
        "last_run_at": 1700000000.0,
    }
    summary = health_summary.summary(payload)
    assert summary["last_run_at"] == 1700000000.0
