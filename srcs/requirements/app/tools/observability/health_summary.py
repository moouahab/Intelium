from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_health(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text() or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def summary(payload: dict) -> dict:
    fetch = payload.get("fetch", {}) or {}
    total = fetch.get("total", 0)
    success = fetch.get("success", 0)
    failure = fetch.get("failure", 0)
    reasons = fetch.get("reasons", {}) or {}
    per_status = fetch.get("per_status", {}) or {}
    recent_errors = fetch.get("recent_errors", []) or []
    bytes_total = int(fetch.get("bytes_total", 0))
    duration_sum = float(fetch.get("duration_sum", 0.0))
    avg_duration = (duration_sum / total) if total else 0.0
    last_run = payload.get("last_run") or {}
    counters = payload.get("counters") or {}
    return {
        "fetch_total": total,
        "fetch_success": success,
        "fetch_failure": failure,
        "fetch_avg_duration": avg_duration,
        "fetch_reasons": reasons,
        "fetch_per_status": per_status,
        "fetch_bytes_total": bytes_total,
        "fetch_recent_errors": recent_errors[-10:],
        "runs_total": counters.get("total", 0),
        "runs_success": counters.get("success", 0),
        "runs_failure": counters.get("failure", 0),
        "last_run_status": last_run.get("status"),
        "last_run_duration": last_run.get("duration_seconds"),
    }


def print_table(s: dict):
    lines = [
        "== Health Summary ==",
        f"Fetch: total={s['fetch_total']} success={s['fetch_success']} failure={s['fetch_failure']} avg_duration={s['fetch_avg_duration']:.2f}s",
        f"Runs: total={s['runs_total']} success={s['runs_success']} failure={s['runs_failure']}",
        f"Dernier run: status={s['last_run_status']} duration={s['last_run_duration']}",
    ]
    print("\n".join(lines))


def print_prometheus(s: dict):
    lines = [
        f"cti_fetch_total {s['fetch_total']}",
        f"cti_fetch_success {s['fetch_success']}",
        f"cti_fetch_failure {s['fetch_failure']}",
        f"cti_fetch_avg_duration_seconds {s['fetch_avg_duration']:.4f}",
        f"cti_fetch_bytes_total {s['fetch_bytes_total']}",
        f"cti_runs_total {s['runs_total']}",
        f"cti_runs_success {s['runs_success']}",
        f"cti_runs_failure {s['runs_failure']}",
    ]
    for reason, count in (s.get("fetch_reasons", {}) or {}).items():
        lines.append(f'cti_fetch_reason_total{{reason="{reason}"}} {count}')
    for status, count in (s.get("fetch_per_status", {}) or {}).items():
        lines.append(f'cti_fetch_status_total{{status="{status}"}} {count}')
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Résumé health.json")
    parser.add_argument("--file", default="data/health.json", help="Chemin du fichier health")
    parser.add_argument("--prometheus", action="store_true", help="Sortie format Prometheus")
    args = parser.parse_args()

    payload = load_health(Path(args.file))
    s = summary(payload)
    if args.prometheus:
        print_prometheus(s)
    else:
        print_table(s)


if __name__ == "__main__":
    main()
