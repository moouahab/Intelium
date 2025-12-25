import json
import sys
from typing import List, Dict, Any


def render_progress(idx: int, total: int, name: str, status: str = ""):
    width = 30
    filled = int(width * idx / total) if total else width
    bar = "=" * filled + ">" + "." * max(0, width - filled - 1)
    sys.stdout.write(f"\r[{bar}] {idx}/{total} {name} {status}")
    sys.stdout.flush()


def print_summary(results: List[Dict[str, Any]], report_path: str | None = None):
    summary = {"sources": results}
    if report_path:
        summary["report"] = report_path
    print(json.dumps(summary, ensure_ascii=False, indent=2))
