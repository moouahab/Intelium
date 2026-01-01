from tools.parsing import parser


def test_parse_content_deduplicate_and_limit():
    scraping_conf = {
        "html": {"deduplicate": True, "max_items": 2, "extract": [{"tag": "p"}]},
        "per_source": {
            "mysite": {
                "html": {
                    "css_selectors": [".item"],
                }
            }
        },
    }
    html = "<div><p>A</p><p>A</p><div class='item'>B</div><div class='item'>C</div></div>"
    results = parser.parse_content("html", html, scraping_conf, source_name="mysite")
    assert results == ["A", "B"]


def test_parse_json_uses_jsonpath_and_limit():
    scraping_conf = {
        "api": {"fields": [{"path": "$.items[*].name"}], "deduplicate": True, "max_items": 3}
    }
    content = '{"items": [{"name": "x"}, {"name": "x"}, {"name": "y"}, {"name": "z"}, {"name": "w"}]}'
    results = parser.parse_content("api", content, scraping_conf)
    assert results == ["x", "y", "z"]


def test_parse_xml_supports_extract_tags_dicts():
    scraping_conf = {"xml": {"extract_tags": [{"tag": "title"}, {"tag": "description"}]}}
    content = "<rss><item><title>A</title><description>Desc</description></item></rss>"
    results = parser.parse_content("xml", content, scraping_conf)
    assert "A" in results
    assert "Desc" in results


def test_extract_iocs_enabled():
    scraping_conf = {"txt": {"extract_iocs": True}}
    content = "CVE-2024-1234 found at http://evil.com from 10.0.0.1"
    results = parser.parse_content("txt", content, scraping_conf)
    assert "CVE-2024-1234" in results
    assert "http://evil.com" in results
    assert "10.0.0.1" in results


def test_sanitize_html_and_xml():
    html_conf = {"html": {"sanitize": True, "extract": [{"tag": "p"}]}}
    html_content = "<html><script>alert(1)</script><p>Bonjour <!--cmt-->monde</p></html>"
    res_html = parser.parse_content("html", html_content, html_conf)
    assert any("alert" not in item for item in res_html)
    assert any("monde" in item for item in res_html)

    xml_conf = {"xml": {"sanitize": True, "extract_tags": [{"tag": "item"}]}}
    xml_content = "<items><!--cmt--><item>Hello<script>ignored</script></item></items>"
    res_xml = parser.parse_content("xml", xml_content, xml_conf)
    assert any("Hello" in item for item in res_xml)
    assert all("ignored" not in item for item in res_xml)


def test_custom_parser_registry_injection():
    calls = {}

    def fake_parser(content, conf):
        calls["content"] = content
        return ["ok-custom"]

    registry = parser.ParserRegistry()
    registry.register("custom", fake_parser)
    conf = {"custom": {}}
    res = parser.parse_content("custom", "payload", conf, parser_registry=registry)
    assert res == ["ok-custom"]
    assert calls["content"] == "payload"


def test_min_chars_filters_short_items():
    scraping_conf = {"html": {"extract": [{"tag": "p"}], "min_chars": 4}}
    html = "<p>ok</p><p>longer</p>"
    results = parser.parse_content("html", html, scraping_conf)
    assert "longer" in results
    assert "ok" not in results
