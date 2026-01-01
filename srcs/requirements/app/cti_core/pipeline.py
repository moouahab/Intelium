from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from cti_core.cli import render_progress, print_summary
from cti_core.scraper import Scraper
from tools.ai_report import generate_ai_report
from tools.extractor import Extractor
from tools.interfaces import CacheBackend
from tools.keywords import find_keyword_hits
from tools.parsers.text_utils import ensure_text
from tools.providers.cache_factory import build_cache
from tools.report import write_report
from tools.result_entry import ResultEntry, normalize_results
from tools.scorer import compute_confidence, score_results


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


def run_extract(results: List[ResultEntry], config_model) -> None:
    extractor = Extractor(config_model.scraping_settings, config_model.keywords)
    for res in results:
        extracted = res.get("extracted") or []
        keywords = res.get("keywords") or None
        if extracted and keywords:
            continue
        if extracted and not keywords:
            hits = find_keyword_hits(extracted, config_model.keywords)
            if hits:
                res["keywords"] = hits
            continue
        saved_path = res.get("saved_path")
        if not saved_path:
            continue
        path = Path(saved_path)
        if not path.exists():
            continue
        try:
            raw_bytes = path.read_bytes()
        except Exception:
            continue
        source_type = res.get("type") or ""
        content: Any = raw_bytes
        if source_type in {"html", "api", "xml", "csv", "txt"}:
            content = ensure_text(raw_bytes)
        extracted_new, keyword_hits = extractor.extract(source_type, content, source_name=res.get("name"))
        if extracted_new and not extracted:
            res["extracted"] = extracted_new
        if keyword_hits and not keywords:
            res["keywords"] = keyword_hits


def prepare_results(results: List[ResultEntry]) -> List[Dict[str, Any]]:
    return normalize_results(results)


def run_score(results_payload: List[Dict[str, Any]], scoring_conf: dict | None = None) -> List[Dict[str, Any]]:
    for res in results_payload:
        if res.get("confidence") is None:
            res["confidence"] = compute_confidence(res)
    if not scoring_conf:
        return results_payload
    try:
        return score_results(
            results_payload,
            weights=scoring_conf.get("weights"),
            per_type_weights=scoring_conf.get("per_type"),
            cvss_conf=scoring_conf.get("cvss"),
        )
    except Exception:
        return results_payload


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
    run_extract(results, config_model)
    results_payload = prepare_results(results)
    scoring_conf = output_conf.get("scoring") or output_conf.get("ai_report", {}).get("scoring")
    results_payload = run_score(results_payload, scoring_conf=scoring_conf)
    report_path = run_report(results_payload, output_conf, logger=logger)
    print_summary(results_payload, report_path=str(report_path))
    return results_payload, report_path
