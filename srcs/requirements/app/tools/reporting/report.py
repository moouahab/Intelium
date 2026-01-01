from pathlib import Path
from typing import List, Dict, Any
from tools.reporting.report_writer import ReportWriter
from tools.interfaces import Reporter
from tools.result_entry import normalize_results
from tools.reporting.exports import export_additional_views


def write_report(results: List[Dict[str, Any]], output_conf: dict, reporter: Reporter | None = None) -> Path:
    results = normalize_results(results)
    reporter = reporter or ReportWriter(output_conf)
    try:
        main_path = reporter.write(results, output_conf)
    except TypeError:
        main_path = reporter.write(results)
    try:
        export_additional_views(results, output_conf, main_path)
    except Exception:
        pass
    return main_path

