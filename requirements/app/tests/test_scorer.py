from tools.scorer import score_results


def test_score_results_adds_priority_and_keeps_input_intact():
    results = [
        {"url": "http://x", "status": "downloaded", "keywords": {"malware": ["ransomware"]}, "extracted": ["CVE-2024-0001 http://example.com"]},
        {"url": "http://y", "status": "error", "keywords": {}, "extracted": []},
    ]
    scored = score_results(results)

    # original not mutated
    assert "score" not in results[0]
    assert "priority" not in results[0]

    assert len(scored) == 2
    assert scored[0]["score"] > scored[1]["score"]
    assert scored[0]["priority"] == "high"
    assert scored[1]["priority"] in {"low", "medium"}
