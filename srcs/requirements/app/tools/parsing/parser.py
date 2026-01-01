from typing import Any, List, Callable, Dict

from tools.parsers.html_parser import parse_html
from tools.parsers.json_parser import parse_json
from tools.parsers.xml_parser import parse_xml
from tools.parsers.csv_parser import parse_csv
from tools.parsers.pdf_parser import parse_pdf
from tools.parsers.ocr_parser import parse_image
from tools.parsers.txt_parser import parse_txt
from tools.parsers.text_utils import ensure_text
from tools.parsing.ioc_extractor import extract_iocs
from tools.parsing.content_sanitizer import sanitize_html, sanitize_xml
from tools.parsers.certkev import extract_certkev_entries, is_certkev_source
from copy import deepcopy
from typing import Optional


PARSERS: dict[str, Callable[[Any, dict], List[str]]] = {
    "html": parse_html,
    "api": parse_json,
    "xml": parse_xml,
    "csv": parse_csv,
    "pdf": parse_pdf,
    "image": parse_image,
    "txt": parse_txt,
}


class ParserRegistry:
    """
    Petit registre injectable pour lier un type à un parseur.
    Permet de surcharger/ajouter des parseurs dans les tests ou extensions.
    """

    def __init__(self, initial: dict[str, Callable[[Any, dict], List[str]]] | None = None):
        self._parsers = dict(initial or {})

    def get(self, name: str) -> Callable[[Any, dict], List[str]] | None:
        return self._parsers.get(name)

    def register(self, name: str, fn: Callable[[Any, dict], List[str]]) -> None:
        self._parsers[name] = fn

    def unregister(self, name: str) -> None:
        self._parsers.pop(name, None)


DEFAULT_PARSER_REGISTRY = ParserRegistry(PARSERS)


def _merge_conf(base: dict, override: dict | None) -> dict:
    merged = deepcopy(base)
    if override:
        for k, v in override.items():
            merged[k] = v
    return merged


def _normalize_results(results: List[Any]) -> List[str]:
    normed: List[str] = []
    seen = set()
    for item in results:
        if not isinstance(item, str):
            continue
        text = " ".join(item.strip().split())
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        normed.append(text)
    return normed


def _filter_cert_like(results: List[str], source_name: str | None) -> List[str]:
    if not source_name:
        return results
    name = source_name.lower()
    if not any(tok in name for tok in ["cert", "kev", "cisa"]):
        return results
    import re

    keep_re = re.compile(r"(CVE-\d{4}-\d{4,7}|CERTFR-\d{4}-ALE|KEV|CISA)", re.IGNORECASE)
    filtered = [r for r in results if keep_re.search(r)]
    return filtered or results


def _post_process(results: List[str], conf: Dict[str, Any], source_name: str | None = None) -> List[str]:
    results = _normalize_results(results)
    results = _filter_cert_like(results, source_name)
    if conf.get("deduplicate", True):
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


def _extract_cvss_if_any(parsed: List[str], raw_content: Any) -> Optional[float]:
    """
    Essaie d'extraire un score CVSS depuis un contenu JSON/API:
    - cherche des clés standards dans l'objet ou dans les extraits si ce sont des dict/JSON.
    Retourne un float si trouvé, sinon None.
    """
    candidates = []

    def _extract_from_obj(obj: Any):
        if isinstance(obj, dict):
            for key in ["cvss", "cvss_score", "baseScore", "cvssBaseScore"]:
                if key in obj:
                    try:
                        return float(obj[key])
                    except (TypeError, ValueError):
                        continue
        return None

    # examiner le contenu brut si c'est du JSON déjà décodé (parse_json retourne des str)
    try:
        import json
        obj = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        candidates.append(_extract_from_obj(obj))
    except Exception:
        pass

    for item in parsed:
        if not isinstance(item, str):
            continue
        # interpréter un extrait comme un nombre ou un dict JSON
        try:
            val = float(item)
            candidates.append(val)
            continue
        except (TypeError, ValueError):
            pass
        try:
            import json
            obj = json.loads(item)
        except Exception:
            obj = None
        if obj:
            candidates.append(_extract_from_obj(obj))
    vals = [c for c in candidates if c is not None]
    return vals[0] if vals else None


def parse_content(
    source_type: str,
    content: Any,
    scraping_conf: dict,
    source_name: str | None = None,
    parser_registry: Optional[ParserRegistry] = None,
) -> List[str]:
    base_conf = scraping_conf.get(source_type, {})
    per_source_conf = {}
    if source_name:
        per_source_conf = (scraping_conf.get("per_source", {}) or {}).get(source_name, {}).get(source_type, {})
    type_conf = _merge_conf(base_conf, per_source_conf)
    registry = parser_registry or DEFAULT_PARSER_REGISTRY
    parser_fn = registry.get(source_type)
    if not parser_fn or content is None:
        return []
    # Normalise l'encodage sur les contenus texte standards
    raw_text_cache: str | None = None
    if source_type in {"api", "xml", "csv", "txt"} and isinstance(content, bytes):
        content = ensure_text(content, encoding=type_conf.get("encoding"))
        raw_text_cache = content
    elif isinstance(content, str):
        raw_text_cache = content
    # Sanitize en amont si demandé (structure conservée)
    if type_conf.get("sanitize"):
        if source_type == "html" and isinstance(content, str):
            content = sanitize_html(content)
        elif source_type == "xml" and isinstance(content, str):
            content = sanitize_xml(content)
    try:
        results = parser_fn(content, type_conf)
        # Extraction CERT/KEV contextualisée si activée ou source identifiée comme telle
        if type_conf.get("certkev") or is_certkev_source(source_name):
            cert_raw = raw_text_cache
            if cert_raw is None and isinstance(content, (bytes, str)):
                cert_raw = ensure_text(content, encoding=type_conf.get("encoding"))
            if cert_raw:
                results = results + extract_certkev_entries(cert_raw)
        cvss_score = None
        if source_type == "api":
            cvss_score = _extract_cvss_if_any(results, content)
        # Extraction IOC optionnelle (CVE/URL/IP) sur les extraits + le contenu brut
        if type_conf.get("extract_iocs"):
            texts = list(results)
            texts.append(ensure_text(content, encoding=type_conf.get("encoding")))
            results = results + extract_iocs(texts, type_conf.get("extract_iocs"))
        if cvss_score is not None:
            results = [f"CVSS:{cvss_score}"] + results
        return _post_process(results, type_conf, source_name=source_name)
    except Exception:
        return []
