import json
from cti_core.config_model import ConfigModel


def test_config_model_builds_sources_and_keywords(tmp_path):
    keywords_path = tmp_path / "data" / "keyword.json"
    keywords_path.parent.mkdir(parents=True, exist_ok=True)
    keywords_path.write_text(json.dumps({"malware": ["test"]}))

    conf_path = tmp_path / "config" / "conf.yaml"
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(
        f"""
        keywords: {keywords_path}
        sources:
          - name: CERT-FR
            url: https://www.cert.ssi.gouv.fr/alerte/
            type: html
        """
    )

    model = ConfigModel(conf_path)

    assert model.keywords == {"malware": ["test"]}
    assert len(model.source_objects) == 1
    assert model.source_objects[0].type == "html"
    assert not model.has_errors()


def test_config_model_unknown_type_and_missing_url(tmp_path):
    keywords_path = tmp_path / "data" / "keyword.json"
    keywords_path.parent.mkdir(parents=True, exist_ok=True)
    keywords_path.write_text(json.dumps({"vulnerability": ["CVE"]}))

    conf_path = tmp_path / "config" / "conf.yaml"
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(
        f"""
        keywords: {keywords_path}
        sources:
          - name: BadType
            url: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
            type: unknown
          - name: MissingUrl
            type: html
        """
    )

    model = ConfigModel(conf_path, strict=True)

    # BadType fallback vers html avec un warning
    assert model.source_objects[0].type == "html"
    assert model.has_warnings()
    # MissingUrl ignoré en mode strict -> une erreur
    assert model.has_errors()


def test_config_model_schedule_loaded(tmp_path):
    keywords_path = tmp_path / "data" / "keyword.json"
    keywords_path.parent.mkdir(parents=True, exist_ok=True)
    keywords_path.write_text(json.dumps({"malware": ["test"]}))

    conf_path = tmp_path / "config" / "conf.yaml"
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    conf_path.write_text(
        f"""
        keywords: {keywords_path}
        scheduling:
          interval: 1h
          retry_on_failure: true
        sources:
          - name: CERT-FR
            url: https://www.cert.ssi.gouv.fr/alerte/
            type: html
        """
    )

    model = ConfigModel(conf_path)

    assert hasattr(model, "yaml_config")
    assert model.yaml_config["scheduling"]["interval"] == "1h"
