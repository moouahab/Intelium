from tools.parsing import parser


def test_cvss_extraction_from_api_results():
    scraping_conf = {"api": {"fields": [{"path": "$.score"}], "extract_iocs": False}}
    content = '{"score": 9.8}'
    results = parser.parse_content("api", content, scraping_conf)
    assert any(item.startswith("CVSS:") for item in results)
    assert "CVSS:9.8" in results
