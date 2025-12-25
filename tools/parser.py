from typing import Any, List, Callable, Dict

from tools.parsers.html_parser import parse_html
from tools.parsers.json_parser import parse_json
from tools.parsers.xml_parser import parse_xml
from tools.parsers.csv_parser import parse_csv
from tools.parsers.pdf_parser import parse_pdf
from tools.parsers.ocr_parser import parse_image
from tools.parsers.txt_parser import parse_txt
from tools.parsers.text_utils import ensure_text
from tools.ioc_extractor import extract_iocs
from tools.content_sanitizer import sanitize_html, sanitize_xml
from copy import deepcopy


PARSERS: dict[str, Callable[[Any, dict], List[str]]] = {
    "html": parse_html,
    "api": parse_json,
    "xml": parse_xml,
    "csv": parse_csv,
    "pdf": parse_pdf,
    "image": parse_image,
    "txt": parse_txt,
}


def _merge_conf(base: dict, override: dict | None) -> dict:
    merged = deepcopy(base)
    if override:
        for k, v in override.items():
            merged[k] = v
    return merged


def _post_process(results: List[str], conf: Dict[str, Any]) -> List[str]:
    if conf.get("deduplicate"):
        seen = set()
        deduped = []
        for item in results:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        results = deduped
    max_items = conf.get("max_items")
    if isinstance(max_items, int) and max_items >= 0:
        results = results[:max_items]
    return results


def parse_content(source_type: str, content: Any, scraping_conf: dict, source_name: str | None = None) -> List[str]:
    base_conf = scraping_conf.get(source_type, {})
    per_source_conf = {}
    if source_name:
        per_source_conf = (scraping_conf.get("per_source", {}) or {}).get(source_name, {}).get(source_type, {})
    type_conf = _merge_conf(base_conf, per_source_conf)
    parser_fn = PARSERS.get(source_type)
    if not parser_fn or content is None:
        return []
    # Normalise l'encodage sur les contenus texte standards
    if source_type in {"api", "xml", "csv", "txt"} and isinstance(content, bytes):
        content = ensure_text(content, encoding=type_conf.get("encoding"))
    # Sanitize en amont si demandé (structure conservée)
    if type_conf.get("sanitize"):
        if source_type == "html" and isinstance(content, str):
            content = sanitize_html(content)
        elif source_type == "xml" and isinstance(content, str):
            content = sanitize_xml(content)
    try:
        results = parser_fn(content, type_conf)
        # Extraction IOC optionnelle (CVE/URL/IP) sur les extraits + le contenu brut
        if type_conf.get("extract_iocs"):
            texts = list(results)
            texts.append(ensure_text(content, encoding=type_conf.get("encoding")))
            results = results + extract_iocs(texts, type_conf.get("extract_iocs"))
        return _post_process(results, type_conf)
    except Exception:
        return []
