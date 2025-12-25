from tools.auth import build_headers


def test_build_headers_uses_hosts_section_only():
    auth_conf = {
        "headers": {"User-Agent": "test-agent"},
        "hosts": {
            "api.example.com": {"Authorization": "Bearer 123"}
        }
    }
    headers = build_headers("https://api.example.com/path", auth_conf)
    assert headers["User-Agent"] == "test-agent"
    assert headers["Authorization"] == "Bearer 123"
    # aucune fallback sur clé legacy
    assert "X-Legacy" not in headers
