import re
from typing import List


CERT_LIKE = re.compile(r"(CVE-\d{4}-\d{4,7}|CERTFR-\d{4}-(ALE|AVI)-\d{3}|KEV|CISA|ICS-CERT)", re.IGNORECASE)


def _clean(text: str) -> str:
    return " ".join(text.split())


def extract_certkev_entries(raw_text: str, max_items: int | None = 50) -> List[str]:
    """
    Extrait des entrées structurées depuis des bulletins CERT/KEV en combinant
    l'identifiant (CVE/CERTFR/KEV) et un court contexte.
    """
    if not raw_text:
        return []
    text = _clean(str(raw_text))
    entries: list[str] = []
    seen: set[str] = set()

    for match in CERT_LIKE.finditer(text):
        start = max(0, match.start() - 160)
        end = min(len(text), match.end() + 200)
        snippet = _clean(text[start:end])
        cves = re.findall(r"CVE-\d{4}-\d{4,7}", snippet, flags=re.IGNORECASE)
        marker = match.group(1).upper()
        label = ", ".join(sorted(set(cv.upper() for cv in cves))) or marker
        entry = f"{label} | {snippet}"[:320]
        key = entry.lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(entry)
        if max_items is not None and len(entries) >= max_items:
            break
    return entries


def is_certkev_source(source_name: str | None) -> bool:
    if not source_name:
        return False
    name = source_name.lower()
    return any(tok in name for tok in ["cert", "kev", "cisa"])
