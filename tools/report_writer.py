from pathlib import Path
from typing import List, Dict, Any
import json
import re
from tools.report_sections import build_markdown_section, build_json_entry


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9-_]+", "-", value.strip())
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-").lower() or "source"


class ReportWriter:
    def __init__(self, output_conf: dict):
        self.output_conf = output_conf or {}
        self.fmt = self.output_conf.get("format", "markdown").lower()
        self.file_path = Path(self.output_conf.get("file", "reports/rapport.md"))
        self.split = bool(self.output_conf.get("split_per_source", True))
        self.detail_dir = Path(self.output_conf.get("detail_dir", self.file_path.parent / "sources"))
        self.language = self.output_conf.get("language", "fr")

        self.strategy = self._build_strategy()

    def _ensure_dirs(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.split:
            self.detail_dir.mkdir(parents=True, exist_ok=True)

    def _markdown_block(
        self,
        res: Dict[str, Any],
        heading_prefix: str,
        detail_path: str | None = None,
        extracted_limit: int | None = None,
        include_keywords: bool = True,
    ) -> List[str]:
        return build_markdown_section(
            res,
            heading_prefix=heading_prefix,
            detail_path=detail_path,
            extracted_limit=extracted_limit,
            include_keywords=include_keywords,
        )

    def _write_markdown_detail(self, res: Dict[str, Any], path: Path):
        lines = self._markdown_block(res, heading_prefix="#", extracted_limit=None, include_keywords=True)
        path.write_text("\n".join(lines))

    def _write_json_detail(self, res: Dict[str, Any], path: Path):
        path.write_text(json.dumps(res, ensure_ascii=False, indent=2))

    def _build_strategy(self):
        if self.fmt == "json":
            return _JsonReportStrategy(self)
        return _MarkdownReportStrategy(self)

    def write(self, results: List[Dict[str, Any]]) -> Path:
        self._ensure_dirs()
        return self.strategy.write_main(results)


class _BaseReportStrategy:
    def __init__(self, writer: ReportWriter):
        self.writer = writer

    def _detail_path(self, res: Dict[str, Any], extension: str) -> Path:
        title = res.get("name") or res.get("url", "source")
        return self.writer.detail_dir / f"{_slugify(title)}{extension}"

    def _should_skip_detail(self, res: Dict[str, Any], path: Path) -> bool:
        return res.get("status") == "skipped-cache" and path.exists()


class _MarkdownReportStrategy(_BaseReportStrategy):
    def write_detail(self, res: Dict[str, Any]) -> Path:
        path = self._detail_path(res, ".md")
        if not self._should_skip_detail(res, path):
            lines = self.writer._markdown_block(res, heading_prefix="#", extracted_limit=None, include_keywords=True)
            path.write_text("\n".join(lines))
        return path

    def write_main(self, results: List[Dict[str, Any]]) -> Path:
        lines = [f"# Rapport CTI ({self.writer.language})", ""]
        for res in results:
            detail_path = None
            if self.writer.split:
                detail_path = str(self.write_detail(res))
            lines.extend(
                self.writer._markdown_block(
                    res,
                    heading_prefix="##",
                    detail_path=detail_path,
                    extracted_limit=5 if not detail_path else 0,
                    include_keywords=not bool(detail_path),
                )
            )
        self.writer.file_path.write_text("\n".join(lines))
        return self.writer.file_path


class _JsonReportStrategy(_BaseReportStrategy):
    def write_detail(self, res: Dict[str, Any]) -> Path:
        path = self._detail_path(res, ".json")
        if not self._should_skip_detail(res, path):
            path.write_text(json.dumps(res, ensure_ascii=False, indent=2))
        return path

    def write_main(self, results: List[Dict[str, Any]]) -> Path:
        payload = {"sources": [], "lang": self.writer.language}
        for res in results:
            detail_path = None
            if self.writer.split:
                detail_path = str(self.write_detail(res))
            entry = build_json_entry(res, detail_path=detail_path)
            payload["sources"].append(entry)
        self.writer.file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        return self.writer.file_path
