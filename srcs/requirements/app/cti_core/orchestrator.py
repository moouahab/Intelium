"""
Boucle d'orchestration/scheduling pour lancer le scraper à intervalle régulier.
Utilisation : python -m scripts.orchestrator --config config/conf.yaml
"""
from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Optional

from tools.config.load_config import load_yaml_config
from tools.scheduling import load_schedule_config, compute_initial_delay
from tools.observability.metrics import RunMetrics, record_run
from cti_core.runner import run


class Orchestrator:
    def __init__(self, config_path: str, metrics_path: str = "data/health.json", logger: Optional[logging.Logger] = None):
        self.config_path = config_path
        self.metrics_path = metrics_path
        self._stop = threading.Event()
        self._running = threading.Lock()
        self.logger = logger or logging.getLogger("orchestrator")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        yaml_conf = load_yaml_config(config_path)
        self.schedule = load_schedule_config(yaml_conf.get("scheduling"))

    def stop(self):
        self._stop.set()

    def _run_once(self):
        if not self._running.acquire(blocking=False):
            return  # déjà en cours
        start = time.time()
        error: Optional[str] = None
        try:
            self.logger.info("Orchestrator run start")
            run(config_path=self.config_path)
        except Exception as exc:  # pragma: no cover - run peut lever tout type d'erreur
            error = str(exc)
            self.logger.error("Run failed: %s", exc)
        finally:
            duration = time.time() - start
            status = "error" if error else "ok"
            record_run(
                self.metrics_path,
                RunMetrics(status=status, started_at=start, duration_seconds=duration, error=error),
            )
            self.logger.info("Orchestrator run end (%s) duration=%.2fs", status, duration)
            self._running.release()

    def _sleep_with_stop(self, seconds: int) -> None:
        for _ in range(int(seconds)):
            if self._stop.is_set():
                break
            time.sleep(1)

    def serve_forever(self):
        first_run = True
        while not self._stop.is_set():
            if self.schedule.start_time:
                delay = compute_initial_delay(self.schedule.start_time, timezone=self.schedule.timezone)
                if delay > 0:
                    self.logger.info(
                        "Waiting %ss before run (start_time=%s, timezone=%s)",
                        delay,
                        self.schedule.start_time,
                        self.schedule.timezone,
                    )
                    self._sleep_with_stop(delay)
            elif not first_run:
                self._sleep_with_stop(self.schedule.interval_seconds)

            if self._stop.is_set():
                break
            self._run_once()
            first_run = False


def run_orchestrator(config_path: str, metrics_path: str = "data/health.json"):
    orch = Orchestrator(config_path=config_path, metrics_path=metrics_path)

    def _handle_signal(signum, frame):  # pragma: no cover - handler runtime
        orch.logger.info("Signal %s received, stopping orchestrator...", signum)
        orch.stop()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    orch.serve_forever()
