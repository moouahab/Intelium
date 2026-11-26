"""Read active ATT&CK techniques as reference records, never as observed incidents."""
import json

from tools.parsers.text_utils import safe_json_load


def parse_stix(content, conf):
    bundle = content if isinstance(content, dict) else safe_json_load(content)
    if not isinstance(bundle, dict) or bundle.get("type") != "bundle":
        return []
    records = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern" or obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        reference = next((ref for ref in obj.get("external_references", [])
                          if ref.get("source_name") in {"mitre-attack", "mitre-mobile-attack", "mitre-ics-attack"}
                          and ref.get("external_id")), None)
        if reference is None:
            continue
        technique_id = reference["external_id"]
        records[technique_id] = {
            "record_kind": "reference", "technique_id": technique_id,
            "name": obj.get("name", ""), "url": reference.get("url", ""),
            "tactics": sorted({p["phase_name"] for p in obj.get("kill_chain_phases", []) if p.get("phase_name")}),
            "platforms": obj.get("x_mitre_platforms", []), "modified": obj.get("modified"),
            "description": obj.get("description", "")[:int(conf.get("max_description_chars", 1000))],
        }
    return [json.dumps(records[key], ensure_ascii=False) for key in sorted(records)]
