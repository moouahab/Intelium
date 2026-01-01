from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import re

from tools.reporting.report_sections import build_markdown_section, build_json_entry, format_status


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9-_]+", "-", value.strip())
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-").lower() or "source"


def is_vuln_entry(res: Dict[str, Any]) -> bool:
    keywords = res.get("keywords") or {}
    if keywords.get("vulnerability"):
        return True
    extracted = res.get("extracted") or []
    for item in extracted:
        if isinstance(item, str) and re.search(r"\bCVE-\d{4}-\d{4,7}\b", item, flags=re.IGNORECASE):
            return True
    return False


class _BaseReporter:
    def __init__(self, output_conf: dict):
        self.output_conf = output_conf or {}
        self.file_path = Path(self.output_conf.get("file", "reports/rapport.md"))
        self.split = bool(self.output_conf.get("split_per_source", True))
        self.detail_dir = Path(self.output_conf.get("detail_dir", self.file_path.parent / "sources"))
        self.language = self.output_conf.get("language", "fr")

    def _ensure_dirs(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.split:
            self.detail_dir.mkdir(parents=True, exist_ok=True)

    def _detail_path(self, res: Dict[str, Any], extension: str) -> Path:
        title = res.get("name") or res.get("url", "source")
        return self.detail_dir / f"{_slugify(title)}{extension}"

    def _should_skip_detail(self, res: Dict[str, Any], path: Path) -> bool:
        return res.get("status") == "skipped-cache" and path.exists()


class MarkdownReporter(_BaseReporter):
    def _summary_block(self, results: List[Dict[str, Any]]) -> List[str]:
        counts: Dict[str, int] = {}
        for res in results:
            status = (res.get("status") or "unknown")
            counts[status] = counts.get(status, 0) + 1
        ordered = [
            "downloaded",
            "skipped-cache",
            "offline",
            "blocked-robots",
            "http-error",
            "error",
            "skipped-quota",
        ]
        ordered_counts = [s for s in ordered if s in counts] + [s for s in counts.keys() if s not in ordered]
        lines = ["## Résumé du run", f"- Sources totales : {len(results)}"]
        if ordered_counts:
            parts = [f"{format_status(s)}={counts[s]}" for s in ordered_counts]
            lines.append("- Statuts : " + ", ".join(parts))
        if "skipped-cache" in counts:
            lines.append("- Note : cache-only = données issues du cache (pas de téléchargement)")
        if "offline" in counts:
            lines.append("- Note : offline = mode cache-only activé sans cache disponible")
        lines.append("")
        return lines

    def write_detail(self, res: Dict[str, Any]) -> Path:
        path = self._detail_path(res, ".md")
        if not self._should_skip_detail(res, path):
            lines = build_markdown_section(res, heading_prefix="#", extracted_limit=None, include_keywords=True)
            path.write_text("\n".join(lines))
        return path

    def write(self, results: List[Dict[str, Any]]) -> Path:
        self._ensure_dirs()
        lines = [f"# Rapport CTI ({self.language})", ""]
        lines.extend(self._summary_block(results))
        for res in results:
            detail_path = None
            if self.split:
                detail_path = str(self.write_detail(res))
            lines.extend(
                build_markdown_section(
                    res,
                    heading_prefix="##",
                    detail_path=detail_path,
                    extracted_limit=5 if not detail_path else 0,
                    include_keywords=not bool(detail_path),
                )
            )
        self.file_path.write_text("\n".join(lines))
        return self.file_path


class JsonReporter(_BaseReporter):
    def write_detail(self, res: Dict[str, Any]) -> Path:
        path = self._detail_path(res, ".json")
        if not self._should_skip_detail(res, path):
            path.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        return path

    def write(self, results: List[Dict[str, Any]]) -> Path:
        self._ensure_dirs()
        payload = {"sources": [], "lang": self.language}
        for res in results:
            detail_path = None
            if self.split:
                detail_path = str(self.write_detail(res))
            entry = build_json_entry(res, detail_path=detail_path)
            payload["sources"].append(entry)
        self.file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return self.file_path


def build_reporter(output_conf: dict):
    fmt = (output_conf.get("format") or "markdown").lower()
    if fmt == "json":
        return JsonReporter(output_conf)
    return MarkdownReporter(output_conf)
