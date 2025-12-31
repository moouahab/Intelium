from tools.parsers.certkev import extract_certkev_entries, is_certkev_source
from tools import parser


def test_extract_certkev_entries_with_context():
    text = (
        "CERTFR-2024-ALE-001 évoque CVE-2024-1234 et CVE-2024-5678. "
        "Patch immédiat recommandé. Plus loin, KEV liste CVE-2024-9999."
    )
    entries = extract_certkev_entries(text, max_items=5)
    assert any("CVE-2024-1234" in e for e in entries)
    assert any("CERTFR-2024-ALE-001" in e for e in entries)
    assert len(entries) <= 5


def test_parser_auto_certkev_on_cert_source():
    scraping_conf = {"html": {"extract": [{"tag": "p"}]}}
    content = "<p>Bulletin CERTFR-2024-ALE-002 pour CVE-2024-8888.</p>"
    res = parser.parse_content("html", content, scraping_conf, source_name="CERT-FR")
    assert any("CVE-2024-8888" in r for r in res)
    assert any("CERTFR-2024-ALE-002" in r for r in res)


def test_is_certkev_source_helper():
    assert is_certkev_source("cert-fr")
    assert is_certkev_source("CISA-KEV")
    assert not is_certkev_source("random")
