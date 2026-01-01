from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from tools.providers.reporters import build_reporter, is_vuln_entry
from tools.result_entry import normalize_results


class ReportWriter:
    def __init__(self, output_conf: dict):
        self.output_conf = output_conf or {}
        self.file_path = Path(self.output_conf.get("file", "reports/rapport.md"))
        self.detail_dir = Path(self.output_conf.get("detail_dir", self.file_path.parent / "sources"))
        self.additional_formats = [fmt.lower() for fmt in (self.output_conf.get("additional_formats") or [])]
        self.vuln_only = bool((self.output_conf.get("filter") or {}).get("vulnerability_only"))

    def write(self, results: List[Dict[str, Any]], output_conf: dict | None = None) -> Path:
        if output_conf is not None and output_conf is not self.output_conf:
            return ReportWriter(output_conf).write(results)
        results = normalize_results(results)
        if self.vuln_only:
            results = [r for r in results if is_vuln_entry(r)]
        reporter = build_reporter(self.output_conf)
        main_path = reporter.write(results)

        # Générer d'autres formats si demandés
        for extra_fmt in self.additional_formats:
            extra_conf = dict(self.output_conf)
            extra_conf["format"] = extra_fmt
            # chemins dérivés : ajoute le suffixe du format si non explicite
            base = self.file_path
            extra_path = base.with_suffix(f".{extra_fmt}") if base.suffix else Path(f"{base}.{extra_fmt}")
            extra_conf["file"] = str(extra_path)
            extra_conf["detail_dir"] = str(Path(extra_conf.get("detail_dir", self.detail_dir)) / extra_fmt)
            extra_conf.pop("additional_formats", None)  # éviter la récursion
            ReportWriter(extra_conf).write(results)
        return main_path
