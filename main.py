import argparse

from cti_core.runner import run


def main():
    parser = argparse.ArgumentParser(description="CTI Scraper")
    parser.add_argument("--config", default="config/conf.yaml", help="Chemin vers le fichier de configuration")
    parser.add_argument("--ai-report", dest="ai_report", action="store_true", help="Forcer l'activation du rapport IA")
    parser.add_argument("--no-ai-report", dest="ai_report", action="store_false", help="Désactiver le rapport IA")
    parser.set_defaults(ai_report=None)
    args = parser.parse_args()
    run(config_path=args.config, force_ai_report=args.ai_report)


if __name__ == "__main__":
    main()
