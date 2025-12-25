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

    def _handle_detail(self, res: Dict[str, Any]) -> str | None:
        if not self.split:
            return None
        title = res.get("name") or res.get("url", "source")
        if self.fmt == "json":
            detail_path = self.detail_dir / f"{_slugify(title)}.json"
            if not (res.get("status") == "skipped-cache" and detail_path.exists()):
                self._write_json_detail(res, detail_path)
        else:
            detail_path = self.detail_dir / f"{_slugify(title)}.md"
            if not (res.get("status") == "skipped-cache" and detail_path.exists()):
                self._write_markdown_detail(res, detail_path)
        return str(detail_path)

    def _write_json_main(self, results: List[Dict[str, Any]]) -> Path:
        payload = {"sources": [], "lang": self.language}
        for res in results:
            entry = build_json_entry(res, detail_path=self._handle_detail(res))
            payload["sources"].append(entry)
        self.file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        return self.file_path

    def _write_markdown_main(self, results: List[Dict[str, Any]]) -> Path:
        lines = [f"# Rapport CTI ({self.language})", ""]
        for res in results:
            title = res.get("name") or res.get("url")
            detail_path = self._handle_detail(res)
            lines.extend(
                self._markdown_block(
                    res,
                    heading_prefix="##",
                    detail_path=detail_path,
                    extracted_limit=5 if not detail_path else 0,
                    include_keywords=not bool(detail_path),
                )
            )
        self.file_path.write_text("\n".join(lines))
        return self.file_path

    def write(self, results: List[Dict[str, Any]]) -> Path:
        self._ensure_dirs()
        if self.fmt == "json":
            return self._write_json_main(results)
        return self._write_markdown_main(results)
