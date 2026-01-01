import logging

from cti_core.config_model import ConfigModel
from cti_core.scraper import Scraper
from tools.load_config import get_config_as_json_string
from tools.cache_factory import build_cache
from tools.interfaces import CacheBackend
from tools.logger_utils import setup_logger, log_structured
from tools.report import write_report
from cti_core.cli import render_progress, print_summary
from tools.ai_report import generate_ai_report
from urllib.parse import urlparse
from tools.preflight import check_env_requirements
from tools.result_entry import normalize_results


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


def build_cache_manager(cache_conf: dict) -> CacheBackend:
    return build_cache(cache_conf)


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

    cache_manager = build_cache_manager(config_model.yaml_config.get("cache", {}))

    total_sources = len(config_model.source_objects)
    render_progress(0, total_sources, "initialisation", "")
    scraper = Scraper(config_model, cache_manager)
    results = scraper.run()
    results_payload = normalize_results(results)
    render_progress(total_sources, total_sources, "terminé", "")
    print()  # fin de barre
    # Rapport et résumé JSON
    output_conf = config_model.yaml_config.get("output", {})
    # override éventuel du flag IA
    if force_ai_report is not None:
        output_conf = dict(output_conf)
        ai_conf = dict(output_conf.get("ai_report", {}))
        ai_conf["enabled"] = force_ai_report
        output_conf["ai_report"] = ai_conf
    report_path = write_report(results_payload, output_conf)
    # Rapport IA optionnel
    ai_conf = output_conf.get("ai_report", {})
    generate_ai_report(results_payload, ai_conf, logger=logger)
    print_summary(results_payload, report_path=str(report_path))
