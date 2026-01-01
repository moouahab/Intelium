#!/usr/bin/env python3
"""
Expose un endpoint HTTP simple pour servir les métriques (health_summary) en texte Prometheus ou JSON.
Usage :
  python scripts/metrics_server.py --file data/health.json --port 9000 --format prometheus
"""
from __future__ import annotations

import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from tools.observability.health_summary import load_health, summary, print_prometheus


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/metrics"):
            self._serve_metrics(prometheus=True)
        elif self.path.startswith("/health"):
            self._serve_metrics(prometheus=False)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_metrics(self, prometheus: bool):
        payload = load_health(Path(self.server.metrics_file))  # type: ignore
        s = summary(payload)
        if prometheus:
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
            last_status = s.get("last_run_status")
            if last_status:
                lines.append(f"cti_last_run_success {1 if last_status == 'ok' else 0}")
                lines.append(f"cti_last_run_failure {1 if last_status != 'ok' else 0}")
            last_duration = s.get("last_run_duration")
            if last_duration is not None:
                lines.append(f"cti_last_run_duration_seconds {float(last_duration):.4f}")
            last_run_at = s.get("last_run_at")
            if last_run_at is not None:
                lines.append(f"cti_last_run_timestamp {float(last_run_at):.0f}")
            for reason, count in (s.get("fetch_reasons", {}) or {}).items():
                lines.append(f'cti_fetch_reason_total{{reason="{reason}"}} {count}')
            for status, count in (s.get("fetch_per_status", {}) or {}).items():
                lines.append(f'cti_fetch_status_total{{status="{status}"}} {count}')
            body = "\n".join(lines)
            content_type = "text/plain; version=0.0.4"
        else:
            body = json.dumps(s, indent=2)
            content_type = "application/json"
        body_bytes = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)


def main():
    parser = argparse.ArgumentParser(description="Expose metrics/health over HTTP")
    parser.add_argument("--file", default="data/health.json", help="Chemin du fichier health.json")
    parser.add_argument("--port", type=int, default=9000, help="Port HTTP")
    args = parser.parse_args()

    handler_cls = MetricsHandler
    server = HTTPServer(("0.0.0.0", args.port), handler_cls)
    server.metrics_file = args.file  # type: ignore
    print(f"Serving metrics on http://0.0.0.0:{args.port}/metrics et /health (file={args.file})")
    server.serve_forever()


if __name__ == "__main__":
    main()
