from tools.auth import build_headers
from tools.auth import load_auth
import os


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


def test_load_auth_env_substitution(tmp_path, monkeypatch):
    monkeypatch.setenv("OTX_TOKEN", "SECRET123")
    auth_file = tmp_path / "auth.yaml"
    auth_file.write_text(
        """
authentication:
  headers:
    X-Api-Key: "${OTX_TOKEN}"
"""
    )
    auth = load_auth(auth_file)
    assert auth["headers"]["X-Api-Key"] == "SECRET123"
