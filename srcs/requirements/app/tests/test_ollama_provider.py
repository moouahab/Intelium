import json
from pathlib import Path

import pytest

from tools.providers.ai.ollama_provider import OllamaProvider, validate_findings
from tools.reporting.threat_evidence import build_evidence, select_evidence
from tools.parsing.parser import parse_content
from tools.reporting.report import write_report


def sources():
    text = json.dumps({"cveID": "CVE-2025-12345", "shortDescription": "Remote code execution affects a public service.",
                       "knownRansomwareCampaignUse": "Unknown", "requiredAction": "Apply vendor updates."})
    return [{"name": "CISA-KEV-CSV", "url": "https://example.com/kev.csv", "type": "csv", "status": "downloaded", "extracted": [text]}]


def finding(evidence):
    return {"evidence_id": evidence[0]["id"], "quote": "Remote code execution affects a public service.",
            "summary": "CVE-2025-12345 concerne une exécution de code.",
            "recommendation": "Vérifier les actifs concernés avant de déployer le correctif éditeur."}


class Response:
    status_code = 200

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class Session:
    def __init__(self, reason="stop", corrupt=False):
        self.reason, self.corrupt = reason, corrupt
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        evidence = json.JSONDecoder().raw_decode(kwargs["json"]["prompt"])[0]["evidence"]
        item = {"evidence_id": evidence[0]["id"], "action_code": evidence[0]["allowed_action"]}
        if self.corrupt:
            item["evidence_id"] = "invented"
        return Response({"done": True, "done_reason": self.reason,
                         "response": json.dumps({"findings": [item]})})


def test_valid_report_archives_and_preserves_technical_report(tmp_path, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://localhost:11434")
    session = Session()
    technical = tmp_path / "rapport.md"
    technical.write_text("TECHNICAL")
    path = OllamaProvider(session).generate(sources(), {"output": str(tmp_path / "rapport_ia.md")})
    assert technical.read_text() == "TECHNICAL"
    quality = json.loads(path.with_suffix(".quality.json").read_text())
    assert quality["validation_status"] == "passed"
    archive = tmp_path / "runs" / quality["run_id"]
    assert all((archive / name).exists() for name in ["request.json", "response.json", "quality.json", "report.md", "evidence.json", "attack_types.csv"])
    assert session.calls[0][1]["allow_redirects"] is False
    assert "FIN DU RAPPORT" in path.read_text()
    import hashlib
    assert hashlib.sha256(path.read_bytes()).hexdigest() == quality["report_sha256"]
    assert hashlib.sha256((archive / "report.md").read_bytes()).hexdigest() == quality["archived_report_sha256"]
    assert f"runs/{quality['run_id']}/evidence.json" in path.read_text()


@pytest.mark.parametrize("reason,corrupt", [("length", False), ("stop", True)])
def test_invalid_output_is_not_published_as_valid(tmp_path, reason, corrupt):
    path = OllamaProvider(Session(reason, corrupt)).generate(sources(), {"output": str(tmp_path / "ai.md")})
    quality = json.loads(path.with_suffix(".quality.json").read_text())
    assert quality["validation_status"] == "failed"
    assert "Action proposée :" not in path.read_text()
    assert "Synthèse IA non validée" in path.read_text()


def test_no_evidence_does_not_call_model(tmp_path):
    session = Session()
    path = OllamaProvider(session).generate([], {"output": str(tmp_path / "ai.md")})
    assert session.calls == []
    assert json.loads(path.with_suffix(".quality.json").read_text())["validation_status"] == "failed"


def test_rejects_invented_identifier_and_quote():
    evidence = build_evidence(sources())
    item = finding(evidence)
    item["summary"] = "CVE-2099-99999 exploite T9999.999 via https://evil.example/"
    item["quote"] = "invented citation, not present in the source"
    errors = validate_findings({"findings": [item]}, evidence)
    assert len(errors) == 3


def test_schema_limits_apply_even_if_model_ignores_them():
    from tools.providers.ai.ollama_provider import MAX_FINDINGS
    evidence = build_evidence(sources())
    assert validate_findings({"findings": [finding(evidence)] * (MAX_FINDINGS + 1)}, evidence)
    item = finding(evidence)
    item["summary"] = "x" * 321
    assert "longueur" in validate_findings({"findings": [item]}, evidence)[0]


def test_quotes_are_copied_by_code_not_rewritten_by_model():
    from tools.providers.ai.ollama_provider import resolve_decisions
    evidence = build_evidence(sources())
    item = {"evidence_id": evidence[0]["id"], "action_code": "verify_exposure"}
    result = resolve_decisions({"findings": [item]}, evidence)
    assert result["findings"][0]["quote"] in evidence[0]["text"]
    assert validate_findings(result, evidence) == []
    with pytest.raises(ValueError):
        resolve_decisions({"findings": [{**item, "quote": "model invented this"}]}, evidence)
    with pytest.raises(ValueError):
        resolve_decisions({"findings": [{**item, "action_code": "retrospective_hunt"}]}, evidence)
    with pytest.raises(ValueError):
        resolve_decisions({"findings": [item, item]}, evidence)


def test_untranslated_summary_is_rejected():
    evidence = build_evidence(sources())
    item = finding(evidence)
    item["summary"] = "Remote code execution affects this product."
    assert any("français" in error for error in validate_findings({"findings": [item]}, evidence))


def test_csv_preserves_headers_comments_sort_and_bom():
    content = '# generated\n\ufeffcveID,dateAdded,shortDescription\nCVE-2024-1111,2024-01-01,"old, row"\nCVE-2025-12345,2025-02-01,new\n'
    conf = {"csv": {"comment_prefix": "#", "record_format": "json", "sort_by": "dateAdded", "descending": True, "max_rows": 1}}
    rows = parse_content("csv", content, conf)
    assert json.loads(rows[0]) == {"cveID": "CVE-2025-12345", "dateAdded": "2025-02-01", "shortDescription": "new"}


def test_stix_excludes_deprecated_and_remains_reference():
    active = {"type": "attack-pattern", "name": "Phishing", "description": "An adversary sends phishing messages.",
              "external_references": [{"source_name": "mitre-attack", "external_id": "T1566"}],
              "kill_chain_phases": [{"phase_name": "initial-access"}]}
    content = json.dumps({"type": "bundle", "objects": [active, {**active, "revoked": True}, {**active, "x_mitre_deprecated": True}]})
    rows = parse_content("stix", content, {})
    assert len(rows) == 1
    evidence = build_evidence([{"name": "MITRE", "url": "https://example.com/attack", "type": "stix", "status": "downloaded", "extracted": rows}])
    assert evidence[0]["kind"] == "reference"
    assert evidence[0]["attack_types"] == ["Hameçonnage"]
    assert evidence[0]["tactics"] == ["initial-access"]


def test_unknown_ransomware_is_not_positive_and_sources_are_diverse():
    evidence = build_evidence(sources())
    assert "Rançongiciel" not in evidence[0]["attack_types"]
    many = [evidence[0]] * 30 + [{**evidence[0], "url": "https://other.example/feed"}]
    selected = select_evidence(many, max_items=2, per_source=3)
    assert len({item["url"] for item in selected}) == 2


def test_exports_exist_even_without_high_priority(tmp_path):
    write_report(sources(), {"file": str(tmp_path / "technical.md"), "split_per_source": False})
    assert (tmp_path / "summary.md").exists()
    assert (tmp_path / "iocs.json").exists()
    assert "score" in (tmp_path / "iocs.csv").read_text().splitlines()[0]


def test_cache_expiry_preserves_offline_replay():
    from types import SimpleNamespace
    from datetime import datetime, timezone
    from cti_core.scraper import Scraper

    scraper = object.__new__(Scraper)
    scraper.cache_max_age = 900
    scraper.policy = SimpleNamespace(offline=False)
    assert scraper._cache_is_fresh(SimpleNamespace(date=datetime.now(timezone.utc).isoformat()))
    assert not scraper._cache_is_fresh(SimpleNamespace(date="2000-01-01T00:00:00Z"))
    assert not scraper._cache_is_fresh(SimpleNamespace(date=None))
    scraper.policy.offline = True
    assert scraper._cache_is_fresh(SimpleNamespace(date="2000-01-01T00:00:00Z"))


def test_old_c2_is_explicitly_historical():
    result = {"name": "FEODO-C2-CSV", "url": "https://example.com/c2", "status": "downloaded", "type": "csv",
              "extracted": [json.dumps({"dst_ip": "192.0.2.1", "c2_status": "online", "last_online": "2000-01-01"})]}
    item = build_evidence([result])[0]
    assert item["freshness"] == "historical_activity"
    assert item["attack_types"] == ["Commande et contrôle"]


@pytest.mark.parametrize("payload,detected", [
    ('{"description":"AutoOpen ThisDocument <script>eval(1)</script>"}', False),
    ('<html><script>eval(1)</script></html>', True),
    ('Sub AutoOpen()\nThisDocument\nEnd Sub', True),
    ('MZpayload', True),
])
def test_yara_distinguishes_reference_data_from_active_formats(tmp_path, payload, detected):
    import shutil
    from tools.providers.http.scanner import run_scan
    if not shutil.which("yara"):
        pytest.skip("YARA executable required (available in the application image)")
    path = tmp_path / "sample"
    path.write_text(payload)
    rules = Path(__file__).resolve().parents[1] / "rules.yar"
    error = run_scan(path, f'yara "{rules}" {{file}}', scanner="yara")
    assert bool(error) is detected
