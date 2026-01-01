from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import csv
import json as _json

from tools.ioc_extractor import extract_iocs
from tools.scorer import score_results


def _export_executive_summary(scored: List[Dict[str, Any]], path: Path) -> None:
    lines = ["# Executive Summary", ""]
    high = [r for r in scored if r.get("priority") == "high"]
    medium = [r for r in scored if r.get("priority") == "medium"]

    def _brief(res: Dict[str, Any]) -> str:
        name = res.get("name") or res.get("url")
        status = res.get("status")
        cves = [e for e in (res.get("extracted") or []) if isinstance(e, str) and "CVE-" in e]
        cves = list(dict.fromkeys(cves))[:5]
        return f"- {name} ({status}) | CVE: {', '.join(cves) if cves else 'N/A'}"

    lines.append("## Priorité haute")
    lines.extend(_brief(r) for r in high[:10] or ["- Aucune"])
    lines.append("")
    lines.append("## Priorité moyenne")
    lines.extend(_brief(r) for r in medium[:10] or ["- Aucune"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def _export_ioc_table(scored: List[Dict[str, Any]], csv_path: Path, json_path: Path) -> None:
    rows = []
    for res in scored:
        texts = res.get("extracted") or []
        iocs = extract_iocs(texts, {"cve": True, "url": True, "ipv4": True})
        rows.append(
            {
                "name": res.get("name"),
                "url": res.get("url"),
                "type": res.get("type"),
                "status": res.get("status"),
                "priority": res.get("priority"),
                "confidence": res.get("confidence"),
                "score": res.get("score"),
                "iocs": ";".join(iocs),
            }
        )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "type", "status", "priority", "confidence", "iocs"])
        writer.writeheader()
        writer.writerows(rows)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_json.dumps(rows, ensure_ascii=False, indent=2))


def export_additional_views(results: List[Dict[str, Any]], output_conf: Dict[str, Any], main_path: Path) -> None:
    scoring_conf = (output_conf.get("ai_report", {}) or {}).get("scoring", {}) or {}
    weights = scoring_conf.get("weights")
    per_type = scoring_conf.get("per_type")
    cvss_conf = scoring_conf.get("cvss")
    scored = score_results(results, weights=weights, per_type_weights=per_type, cvss_conf=cvss_conf)
    exports = output_conf.get("exports") or {}
    exec_path = Path(exports.get("executive_summary", main_path.parent / "summary.md"))
    ioc_csv = Path(exports.get("ioc_csv", main_path.parent / "iocs.csv"))
    ioc_json = Path(exports.get("ioc_json", main_path.parent / "iocs.json"))
    _export_executive_summary(scored, exec_path)
    _export_ioc_table(scored, ioc_csv, ioc_json)
