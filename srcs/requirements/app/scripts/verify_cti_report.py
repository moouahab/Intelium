#!/usr/bin/env python3
"""Fetch structured public feeds and verify Ollama, without scheduler, Mongo or email."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cti_core.config_model import ConfigModel
from tools.providers.http.client import HttpClient
from tools.parsing.parser import parse_content
from tools.providers.ai.ai_report import generate_ai_report
from tools.reporting.report import write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/conf.yaml")
    parser.add_argument("--output-dir", default="reports/verification")
    parser.add_argument("--collect-only", action="store_true", help="Vérifier les sources sans appeler Ollama")
    parser.add_argument("--results", type=Path, help="Rejouer un fichier results.json de vérification sans collecte")
    args = parser.parse_args()
    model = ConfigModel(args.config)
    if model.errors:
        raise ValueError("; ".join(model.errors))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "raw").mkdir(exist_ok=True)
    client = HttpClient(replace(model.network_policy, metrics_path=None), respect_robots=True, retries=0)
    selected = {"CISA-KEV-CSV", "FEODO-C2-CSV", "MITRE-ATTACK-ENTERPRISE"}
    results = []
    for source in ([] if args.results else model.sources):
        if source.get("name") not in selected:
            continue
        response = client.fetch(source)
        content = response.content
        raw = content.encode("utf-8") if isinstance(content, str) else content or b""
        artifact = None
        if response.status == "downloaded":
            artifact = output / "raw" / (source["name"] + {"csv": ".csv", "stix": ".json"}[source["type"]])
            artifact.write_bytes(raw)
        extracted = parse_content(source["type"], content, model.scraping_settings, source_name=source["name"]) if response.status == "downloaded" else []
        results.append({**source, "status": response.status, "error": response.error,
                        "extracted": extracted, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "artifact": str(artifact) if artifact else None,
                        "content_sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": response.size_bytes})
        print(json.dumps({"source": source["name"], "status": response.status, "extracted": len(extracted), "error": response.error}), flush=True)
    if args.results:
        results = json.loads(args.results.read_text(encoding="utf-8"))
    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(results, {"file": str(output / "technical.md"), "additional_formats": ["json"], "split_per_source": False})
    if args.collect_only:
        return 0 if len(results) == len(selected) and all(item["status"] == "downloaded" and item["extracted"] for item in results) else 1
    ai_conf = {**model.yaml_config["output"]["ai_report"], "output": str(output / "rapport_ia.md")}
    path = generate_ai_report(results, ai_conf)
    quality = json.loads(path.with_suffix(".quality.json").read_text())
    successful = sum(item["status"] == "downloaded" and bool(item["extracted"]) for item in results)
    print(json.dumps({"report": str(path), "validation": quality["validation_status"],
                      "sources_with_data": successful, "sources_expected": len(selected), "errors": quality["errors"]}), flush=True)
    return 0 if quality["validation_status"] == "passed" and successful == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
