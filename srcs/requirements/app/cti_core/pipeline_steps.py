from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from tools.extractor import Extractor
from tools.keywords import find_keyword_hits
from tools.parsers.text_utils import ensure_text
from tools.result_entry import ResultEntry
from tools.scorer import compute_confidence, score_results


_TEXT_TYPES = {"html", "api", "xml", "csv", "txt"}


def enrich_results(results: List[ResultEntry], config_model) -> None:
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
        if source_type in _TEXT_TYPES:
            content = ensure_text(raw_bytes)
        extracted_new, keyword_hits = extractor.extract(source_type, content, source_name=res.get("name"))
        if extracted_new and not extracted:
            res["extracted"] = extracted_new
        if keyword_hits and not keywords:
            res["keywords"] = keyword_hits


def score_results_payload(results_payload: List[Dict[str, Any]], scoring_conf: dict | None = None) -> List[Dict[str, Any]]:
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
