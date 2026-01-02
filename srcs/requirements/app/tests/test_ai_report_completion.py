from tools.providers.ai.ai_report import _is_complete


def test_is_complete_requires_marker():
    assert not _is_complete(None)
    assert not _is_complete("")
    assert not _is_complete("FIN DU")
    assert _is_complete("ok FIN DU RAPPORT")


def test_is_complete_normalizes_accents():
    text = "Résumé exécutif\nFIN DU RAPPORT"
    assert _is_complete(text, required_sections=["Resume executif"])
