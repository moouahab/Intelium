import os
import json
import pytest
from tools.load_config import (
    load_yaml_config,
    get_config_as_json_string,
    load_keywords_from_config,
)

@pytest.fixture
def sample_yaml_file(tmp_path):
    yaml_content = """
    keywords: data/keywords.json
    logging:
      level: INFO
    """
    yaml_path = tmp_path / "config/conf.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(yaml_content)
    return yaml_path

@pytest.fixture
def sample_keyword_file(tmp_path):
    keywords = {
        "malware": ["ransomware", "trojan"],
        "vulnerability": ["CVE-2023-1234"]
    }
    json_path = tmp_path / "data/keywords.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(keywords))
    return json_path

def test_load_yaml_config(sample_yaml_file):
    config = load_yaml_config(sample_yaml_file)
    assert isinstance(config, dict)
    assert config.get("keywords") == "data/keywords.json"

def test_get_config_as_json_string():
    dummy_config = {"a": 1, "b": {"c": 2}}
    json_str = get_config_as_json_string(dummy_config)
    assert isinstance(json_str, str)
    assert '"a": 1' in json_str

def test_load_keywords_from_config(tmp_path, sample_keyword_file):
    yaml_content = f"keywords: {sample_keyword_file}"
    yaml_path = tmp_path / "config/conf.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(yaml_content)
    config = load_yaml_config(yaml_path)
    keywords = load_keywords_from_config(config)
    assert isinstance(keywords, dict)
    assert "malware" in keywords


def test_load_keywords_from_config_with_fallback(tmp_path):
    # Chemin erroné dans la config, mais un fallback existe
    config = {"keywords": "data/keuwords.json"}
    fallback_file = tmp_path / "data/keyword.json"
    fallback_file.parent.mkdir(parents=True, exist_ok=True)
    fallback_file.write_text(json.dumps({"fallback": ["value"]}))

    keywords = load_keywords_from_config(config, default_path=fallback_file)

    assert keywords == {"fallback": ["value"]}


def test_load_yaml_config_with_include(tmp_path):
    base_config = """
    keywords: data/keywords.json
    logging:
      level: INFO
      options:
        console: true
    include:
      - modules/sources.yaml
    """
    include_config = """
    sources:
      - name: CERT-FR
        url: https://www.cert.ssi.gouv.fr/alerte/
    logging:
      level: DEBUG
      options:
        file: logs/app.log
    """

    conf_path = tmp_path / "config" / "conf.yaml"
    include_path = tmp_path / "config" / "modules" / "sources.yaml"
    include_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(base_config)
    include_path.write_text(include_config)

    config = load_yaml_config(conf_path)

    assert config["keywords"] == "data/keywords.json"
    assert config["sources"][0]["name"] == "CERT-FR"
    assert config["logging"]["level"] == "DEBUG"  # valeur de l'include prioritaire
    # merge récursif : options console conservée, fichier ajouté
    assert config["logging"]["options"]["console"] is True
    assert config["logging"]["options"]["file"] == "logs/app.log"


def test_load_yaml_config_merges_lists(tmp_path):
    base_config = """
    include:
      - extra.yaml
    sources:
      - name: BASE
        url: https://base.example
    """
    include_config = """
    sources:
      - name: EXTRA
        url: https://extra.example
    """
    conf_path = tmp_path / "config" / "conf.yaml"
    include_path = tmp_path / "config" / "extra.yaml"
    include_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(base_config)
    include_path.write_text(include_config)

    config = load_yaml_config(conf_path)

    assert [s["name"] for s in config["sources"]] == ["BASE", "EXTRA"]
