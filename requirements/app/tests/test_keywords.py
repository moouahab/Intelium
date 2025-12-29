from tools.keywords import find_keyword_hits


def test_find_keyword_hits_basic():
    keywords = {"vulnerability": ["CVE-2024-0001", "overflow"], "actor": ["APT"]}
    texts = ["Nouvelle CVE-2024-0001 annoncée", "Risque d'overflow détecté"]

    hits = find_keyword_hits(texts, keywords)

    assert hits["vulnerability"] == ["CVE-2024-0001", "overflow"]
    assert "actor" not in hits


def test_find_keyword_hits_handles_noise_and_case():
    keywords = {"indicator": ["IoC", "domain"], "misc": ["Test"]}
    texts = ["ioc trouvé", "DOMAIN détecté", None, 123]

    hits = find_keyword_hits(texts, keywords)

    assert set(hits["indicator"]) == {"domain", "IoC"}
    assert "misc" not in hits
