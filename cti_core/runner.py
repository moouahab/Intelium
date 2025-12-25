from cti_core.config_model import ConfigModel
from cti_core.scraper import Scraper
from tools.load_config import get_config_as_json_string
from tools.cache_factory import build_cache
from tools.cache import CacheManager, CacheRegistry
from tools.logger_utils import setup_logger
from tools.report import write_report
from cti_core.cli import render_progress, print_summary
from tools.ai_report import generate_ai_report


def build_cache_manager(cache_conf: dict) -> CacheManager | CacheRegistry:
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

    if config_model.has_errors():
        for error in config_model.errors:
            logger.error("Erreur configuration : %s", error)
        logger.error("Arrêt du run : configuration invalide.")
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
    report_path = write_report(results, output_conf)
    # Rapport IA optionnel
    ai_conf = output_conf.get("ai_report", {})
    generate_ai_report(results, ai_conf, logger=logger)
    print_summary(results, report_path=str(report_path))
