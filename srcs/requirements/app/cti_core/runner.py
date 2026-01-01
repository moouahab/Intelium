import logging

from cti_core.config_model import ConfigModel
from cti_core.pipeline import run_pipeline
from tools.config.load_config import get_config_as_json_string
from tools.logger_utils import setup_logger, log_structured
from tools.ai_report import generate_ai_report
from urllib.parse import urlparse
from tools.preflight import check_env_requirements


def _validate_allowlist(config_model: ConfigModel, logger) -> bool:
    allow = config_model.network_policy.allow_domains or set()
    if not allow:
        allow = config_model.crawler_settings.get("allow_domains") or set()
    if not allow:
        return True
    invalid = []
    for src in config_model.source_objects:
        host = urlparse(src.url).hostname
        if not host or host not in allow:
            invalid.append((src.name or src.url, src.url, host))
    if invalid:
        msg = "; ".join([f"{name} ({url}) host={host}" for name, url, host in invalid])
        logger.error("Sources hors allowlist : %s", msg)
        return False
    return True


def run(config_path: str = "config/conf.yaml", force_ai_report: bool | None = None):
    try:
        config_model = ConfigModel(config_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erreur de configuration : {exc}")
        return

    logger = setup_logger(config_model.yaml_config.get("logging", {}))

    if config_model.has_warnings():
        for warning in config_model.warnings:
            logger.warning("Avertissement configuration : %s", warning)
        log_structured(logger, logging.WARNING, "config_warnings", warnings=config_model.warnings)

    if config_model.has_errors():
        for error in config_model.errors:
            logger.error("Erreur configuration : %s", error)
        log_structured(logger, logging.ERROR, "config_errors", errors=config_model.errors)
        logger.error("Arrêt du run : configuration invalide.")
        return
    if not check_env_requirements(config_model.yaml_config, config_model.auth_settings, logger=logger):
        logger.error("Arrêt du run : variables d'environnement manquantes.")
        return
    if not _validate_allowlist(config_model, logger):
        logger.error("Arrêt du run : allowlist non respectée.")
        return

    json_config_str = get_config_as_json_string(config_model.yaml_config)
    logger.info("✅ Config chargée.")
    logger.debug(json_config_str)
    logger.info("🔑 Catégories de mots-clés : %s", list(config_model.keywords.keys()))
    logger.info("🌐 Sources configurées : %s", [src.get("name") for src in config_model.sources])

    run_pipeline(config_model, logger=logger, force_ai_report=force_ai_report)
