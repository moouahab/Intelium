from tools.parsers.text_utils import ensure_text, safe_json_load, safe_csv_rows
from tools.parsing.parser import parse_content


def test_ensure_text_handles_bytes_and_newlines():
    raw = b"ligne1\r\nligne2"
    assert ensure_text(raw) == "ligne1\nligne2"


def test_safe_json_load_with_invalid_json_returns_none():
    assert safe_json_load("not-json") is None


def test_safe_csv_rows_parses_delimiter_and_encoding():
    raw = "a;b\n1;2"
    rows = safe_csv_rows(raw, delimiter=";")
    assert rows == [["a", "b"], ["1", "2"]]


def test_parse_content_handles_bytes_for_api_and_csv():
    # JSON bytes
    res_json = parse_content("api", b'{"key": "value"}', {"api": {"fields": [{"path": "$.key"}]}})
    assert res_json == ["value"]
    # CSV bytes
    csv_bytes = b"a,b\n1,2"
    res_csv = parse_content("csv", csv_bytes, {"csv": {"has_header": True}})
    assert "1, 2" in res_csv
