from __future__ import annotations

import re
from typing import Iterable, List, Dict


DEFAULT_PATTERNS = {
    "cve": re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    "url": re.compile(r"https?://[^\s)'\"<>]+", re.IGNORECASE),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),
}


def _enabled_map(options) -> Dict[str, bool]:
    """
    Normalise la config extract_iocs.
    - bool => tous les patterns activés ou désactivés
    - dict => active uniquement les clés truthy (cve/url/ipv4)
    """
    if isinstance(options, bool):
        return {name: options for name in DEFAULT_PATTERNS.keys()}
    if isinstance(options, dict):
        return {name: bool(options.get(name, False)) for name in DEFAULT_PATTERNS.keys()}
    return {}


def extract_iocs(texts: Iterable[str], options) -> List[str]:
    """
    Extrait des IOC simples (CVE, URLs, IPv4) à partir d'une liste de textes.
    Utilise des regex rapides pour limiter les faux positifs.
    """
    enabled = _enabled_map(options)
    if not enabled or not any(enabled.values()):
        return []

    seen = set()
    results: List[str] = []

    def _add(match: str):
        if match in seen:
            return
        seen.add(match)
        results.append(match)

    for text in texts:
        if not isinstance(text, str):
            continue
        for name, pattern in DEFAULT_PATTERNS.items():
            if not enabled.get(name):
                continue
            for m in pattern.findall(text):
                _add(m.strip())
    return results
