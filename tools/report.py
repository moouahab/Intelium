from pathlib import Path
from typing import List, Dict, Any
from tools.report_writer import ReportWriter


def write_report(results: List[Dict[str, Any]], output_conf: dict) -> Path:
    return ReportWriter(output_conf).write(results)
