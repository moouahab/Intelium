import argparse
from cti_core.orchestrator import run_orchestrator


def main():
    parser = argparse.ArgumentParser(description="Orchestrateur CTI Scraper")
    parser.add_argument("--config", default="config/conf.yaml", help="Chemin de la configuration principale")
    parser.add_argument("--metrics", default="data/health.json", help="Chemin du fichier de métriques/health")
    args = parser.parse_args()
    run_orchestrator(config_path=args.config, metrics_path=args.metrics)


if __name__ == "__main__":
    main()
