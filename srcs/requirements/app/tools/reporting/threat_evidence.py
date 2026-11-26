"""Deterministic evidence and attack-type inventory with explicit provenance."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re


# Labels describe mentions in published intelligence, not detections on an asset.
ATTACK_TYPES = {
    "Hameçonnage": r"\b(phishing|spearphishing|hameçonnage)\b",
    "Rançongiciel": r"\b(ransomware|rançongiciel)\b",
    "Déni de service": r"\b(ddos|denial.of.service|déni de service)\b",
    "Vol d’identifiants": r"\b(credential theft|credential dumping|password spraying|vol d.identifiants)\b",
    "Exécution de code": r"\b(remote code execution|arbitrary code execution|exécution de code)\b",
    "Injection SQL": r"\b(sql injection|injection sql)\b",
    "Élévation de privilèges": r"\b(privilege escalation|élévation de privilèges)\b",
    "Exfiltration": r"\b(exfiltration)\b",
    "Chaîne d’approvisionnement": r"\b(supply.chain|chaîne d.approvisionnement)\b",
    "Commande et contrôle": r"\b(command.and.control|botnet|commande et contrôle)\b",
}
PATTERNS = {name: re.compile(pattern, re.I) for name, pattern in ATTACK_TYPES.items()}
IDENTIFIERS = re.compile(r"\b(?:CVE-\d{4}-\d{4,7}|T\d{4}(?:\.\d{3})?)\b", re.I)


def build_evidence(results):
    evidence = {}
    today = datetime.now(timezone.utc).date()
    for source in results:
        if source.get("status") not in {"downloaded", "skipped-cache"}:
            continue
        for text in source.get("extracted") or []:
            if not isinstance(text, str) or not text.strip():
                continue
            try:
                record = json.loads(text)
            except (ValueError, TypeError):
                record = {}
            record = record if isinstance(record, dict) else {}
            reference = source.get("type") == "stix"
            # KEV's field name mentions ransomware even when its value is Unknown.
            searchable = " ".join(str(value) for key, value in record.items()
                                  if key != "knownRansomwareCampaignUse") if record else text
            types = {label for label, pattern in PATTERNS.items() if pattern.search(searchable)}
            if record.get("knownRansomwareCampaignUse") == "Known":
                types.add("Rançongiciel")
            if source.get("name") == "FEODO-C2-CSV" and record.get("dst_ip"):
                types.add("Commande et contrôle")
            freshness = "not_assessed"
            if source.get("name") == "FEODO-C2-CSV":
                try:
                    last_seen = datetime.fromisoformat(record["last_online"]).date()
                    freshness = "historical_activity" if (today - last_seen).days > 30 else "recently_reported"
                except (KeyError, ValueError, TypeError):
                    freshness = "unknown_activity_date"
            digest = hashlib.sha256((str(source.get("url")) + "\n" + text).encode()).hexdigest()
            evidence.setdefault(digest, {
                "id": "E-" + digest[:16], "sha256": digest,
                "source": source.get("name"), "url": source.get("url"),
                "status": source.get("status"), "kind": "reference" if reference else "published_intelligence",
                "retrieved_at": source.get("retrieved_at"), "content_sha256": source.get("content_sha256"),
                "freshness": freshness,
                "context": {key: record[key] for key in ("cveID", "vendorProject", "product", "dst_ip", "dst_port", "malware", "last_online", "technique_id", "name") if key in record},
                "text": text, "attack_types": sorted(types),
                "identifiers": sorted(set(IDENTIFIERS.findall(text))),
                "tactics": record.get("tactics", []) if reference else [],
                "date": record.get("dateAdded") or record.get("last_online") or record.get("modified"),
                "required_action": record.get("requiredAction"),
            })
    return list(evidence.values())


def select_evidence(evidence, max_items=12, per_source=3, max_chars=1200):
    """Round robin prevents a large first feed from hiding all other sources."""
    groups = {}
    for item in evidence:
        if len(item["text"].strip()) < 20:
            continue
        groups.setdefault(item["url"], []).append(item)
    selected = []
    for index in range(per_source):
        for group in groups.values():
            if index < len(group) and len(selected) < max_items:
                selected.append({**group[index], "text": group[index]["text"][:max_chars]})
    return selected


def coverage(results, evidence):
    return {
        "source_count": len(results),
        "statuses": dict(Counter(source.get("status", "unknown") for source in results)),
        "evidence_count": len(evidence),
        "reference_count": sum(item["kind"] == "reference" for item in evidence),
        "sources": [{"name": source.get("name"), "url": source.get("url"),
                     "status": source.get("status"), "error": source.get("error"),
                     "extracted_count": len(source.get("extracted") or [])} for source in results],
    }
