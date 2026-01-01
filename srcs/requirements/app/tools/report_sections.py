from __future__ import annotations

from typing import Any, Dict, List

MAX_SNIPPET_LEN = 300


_STATUS_LABELS = {
    "skipped-cache": "cache-only",
    "offline": "offline (cache-only)",
    "skipped-quota": "quota atteint",
}


def _truncate(text: str, max_len: int = MAX_SNIPPET_LEN) -> str:
    if not isinstance(text, str):
        return text
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def format_status(status: str | None) -> str:
    status = status or "unknown"
    if status == "skipped-cache":
        return f"{_STATUS_LABELS[status]} ({status})"
    label = _STATUS_LABELS.get(status)
    return label or status


def build_markdown_section(
    res: Dict[str, Any],
    heading_prefix: str,
    detail_path: str | None = None,
    extracted_limit: int | None = None,
    include_keywords: bool = True,
) -> List[str]:
    lines = [f"{heading_prefix} {res.get('name') or res.get('url')}"]
    lines.append(f"- Type : {res.get('type')}")
    lines.append(f"- Statut : {format_status(res.get('status'))}")
    if res.get("error"):
        lines.append(f"- Erreur : {res.get('error')}")
    if res.get("saved_path"):
        lines.append(f"- Fichier : {res.get('saved_path')}")
    if detail_path:
        lines.append(f"- Détail : {detail_path}")
    extracted = res.get("extracted") or []
    if extracted and extracted_limit != 0:
        lines.append("- Extraits :")
        limit = extracted_limit if extracted_limit is not None else len(extracted)
        for item in extracted[:limit]:
            lines.append(f"  - {_truncate(item)}")
    keywords = res.get("keywords") or {}
    if keywords and include_keywords:
        lines.append("- Mots-clés :")
        for category, words in keywords.items():
            lines.append(f"  - {category}: {', '.join(words)}")
    lines.append("")
    return lines


def build_json_entry(res: Dict[str, Any], detail_path: str | None = None) -> Dict[str, Any]:
    entry = dict(res)
    if detail_path:
        entry["detail_path"] = detail_path
    return entry
