"""
Scoring heuristique des résultats pour aider la priorisation dans les rapports IA.
Ne remplace pas l'analyse humaine : fournit seulement un ordre d'importance simple.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional
import re

IOC_PATTERNS = {
    "cve": re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    "url": re.compile(r"https?://[^\s)'\"<>]+", re.IGNORECASE),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),
}

DEFAULT_KEYWORD_WEIGHTS = {
    "malware": 30,
    "vulnerability": 25,
    "attack_technique": 20,
}


def _count_iocs(texts: Iterable[str]) -> int:
    seen = set()
    for text in texts:
        if not isinstance(text, str):
            continue
        for pattern in IOC_PATTERNS.values():
            for match in pattern.findall(text):
                seen.add(match)
    return len(seen)


def _has_cve(texts: Iterable[str]) -> bool:
    for text in texts:
        if not isinstance(text, str):
            continue
        if IOC_PATTERNS["cve"].search(text):
            return True
    return False


def _priority_from_score(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def _compute_score(res: Dict[str, Any], weights: Dict[str, int], per_type: Optional[Dict[str, Dict[str, int]]] = None) -> int:
    score = 0
    status = res.get("status")
    if status == "downloaded":
        score += 10
    elif status in {"http-error", "error", "blocked-robots"}:
        score -= 20
    elif status == "skipped-cache":
        score += 5

    keywords = res.get("keywords") or {}
    # poids par type (optionnel)
    source_type = res.get("type")
    type_weights = per_type.get(source_type, {}) if per_type else {}
    for cat, hits in keywords.items():
        weight = type_weights.get(cat, weights.get(cat, weights.get("default", 0)))
        if hits:
            score += weight

    extracted = res.get("extracted") or []
    if extracted:
        score += 5
        score += min(_count_iocs(extracted) * 5, 20)
    return score


def score_results(
    results: List[Dict[str, Any]],
    weights: Optional[Dict[str, int]] = None,
    per_type_weights: Optional[Dict[str, Dict[str, int]]] = None,
    cvss_conf: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retourne une copie des résultats avec deux champs supplémentaires :
    - score (int) : heuristique de priorité
    - priority (str) : high/medium/low
    """
    scored: List[Dict[str, Any]] = []
    weights = weights or DEFAULT_KEYWORD_WEIGHTS
    cvss_enabled = bool(cvss_conf.get("enabled")) if cvss_conf else False
    high_thr = float(cvss_conf.get("high_threshold", 9.0)) if cvss_enabled else None
    med_thr = float(cvss_conf.get("medium_threshold", 7.0)) if cvss_enabled else None
    for res in results:
        entry = deepcopy(res)
        s = _compute_score(entry, weights, per_type=per_type_weights)
        entry["score"] = s
        has_malware = bool(entry.get("keywords", {}).get("malware"))
        has_cve = _has_cve(entry.get("extracted") or [])
        priority = _priority_from_score(s)
        if entry.get("status") == "downloaded" and has_malware and has_cve:
            entry["priority"] = "high"
        else:
            entry["priority"] = priority

        # Si un score CVSS est présent (via extracted/keywords enrichis), ajuster la priorité
        if cvss_enabled:
            cvss_val = entry.get("cvss") or entry.get("cvss_score")
            try:
                cvss = float(cvss_val)
            except (TypeError, ValueError):
                cvss = None
            if cvss is not None:
                if high_thr is not None and cvss >= high_thr:
                    entry["priority"] = "high"
                elif med_thr is not None and cvss >= med_thr and entry["priority"] != "high":
                    entry["priority"] = "medium"
        scored.append(entry)
    return scored
