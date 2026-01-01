from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from cti_core.cli import render_progress, print_summary
from cti_core.scraper import Scraper
from tools.providers.ai.ai_report import generate_ai_report
from tools.interfaces import CacheBackend
from tools.providers.cache_factory import build_cache
from tools.reporting.report import write_report
from tools.result_entry import ResultEntry, normalize_results
from cti_core.pipeline_steps import enrich_results, score_results_payload


def build_cache_manager(cache_conf: dict) -> CacheBackend:
    return build_cache(cache_conf)


def run_fetch(config_model, cache_manager: CacheBackend) -> List[ResultEntry]:
    total_sources = len(config_model.source_objects)
    render_progress(0, total_sources, "initialisation", "")
    scraper = Scraper(config_model, cache_manager)
    results = scraper.run()
    render_progress(total_sources, total_sources, "terminé", "")
    print()  # fin de barre
    return results


def prepare_results(results: List[ResultEntry]) -> List[Dict[str, Any]]:
    return normalize_results(results)


def build_output_conf(base_conf: dict, force_ai_report: bool | None = None) -> dict:
    output_conf = dict(base_conf or {})
    if force_ai_report is not None:
        ai_conf = dict(output_conf.get("ai_report", {}))
        ai_conf["enabled"] = force_ai_report
        output_conf["ai_report"] = ai_conf
    return output_conf


def run_report(results_payload: List[Dict[str, Any]], output_conf: dict, logger=None) -> Path:
    report_path = write_report(results_payload, output_conf)
    ai_conf = output_conf.get("ai_report", {})
    generate_ai_report(results_payload, ai_conf, logger=logger)
    return report_path


def run_pipeline(config_model, logger=None, force_ai_report: bool | None = None) -> Tuple[List[Dict[str, Any]], Path]:
    cache_manager = build_cache_manager(config_model.yaml_config.get("cache", {}))
    results = run_fetch(config_model, cache_manager)
    output_conf = build_output_conf(config_model.yaml_config.get("output", {}), force_ai_report=force_ai_report)
    enrich_results(results, config_model)
    results_payload = prepare_results(results)
    scoring_conf = output_conf.get("scoring") or output_conf.get("ai_report", {}).get("scoring")
    results_payload = score_results_payload(results_payload, scoring_conf=scoring_conf)
    report_path = run_report(results_payload, output_conf, logger=logger)
    print_summary(results_payload, report_path=str(report_path))
    return results_payload, report_path
