# Déploiement & Supervision

## Prérequis
- Python 3.10+
- Dépendances du projet (voir `requirements.txt`)

## Lancement
- Commande : `python3 main.py --config config/conf.yaml`
- Flags utiles : `--ai-report` / `--no-ai-report` pour activer/désactiver le rapport IA sans modifier la config.
- S’assurer que `config/auth.yaml` et `config/output.yaml` sont renseignés (ne pas committer les secrets).

## Service (exemple systemd)
`/etc/systemd/system/cti-scraper.service`
```ini
[Unit]
Description=CTI Scraper

[Service]
WorkingDirectory=/opt/cti-scraper
ExecStart=/usr/bin/python3 /opt/cti-scraper/main.py --config /opt/cti-scraper/config/conf.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Ensuite :
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cti-scraper
```

## Logs & rotation
- Configurer `config/logging.yaml` pour pointer vers un fichier log (RotatingFileHandler est déjà utilisé dans `tools/logger_utils.py`).
- Vérifier les permissions du répertoire de logs.
- Niveaux : passer `level: DEBUG` en cas de diagnostic, revenir à `INFO`/`WARNING` en production.
- Vérifier la rotation (taille max ~1 Mo) et ajuster si besoin.

## Supervision
- Surveiller les fichiers de log (erreurs réseau, robots, cache).
- Vérifier régulièrement le cache (`data/cache.json` ou dossiers par site si `per_site`).
- En cas de rapport IA activé, surveiller la disponibilité du binaire local (`ollama`, `llama`, etc.).
- Santé basique : scripter un “smoke test” (ex. `PYTHONPATH=. python -m pytest tests/test_e2e_report.py`) ou un run sur un petit set de sources de test pour valider l’environnement.
- Intégration monitoring : exporter les statuts de scrape (succès/erreurs) via un script qui lit `data/cache.json` et envoie vers Prometheus/ELK si besoin.
- Runbook : voir `docs/RUNBOOK.md` pour les vérifications post-redémarrage et les tests par service.

## Sécurité & secrets
- Ne pas committer `config/auth.yaml`.
- Utiliser des variables d’environnement ou un vault pour injecter les clés.
- Bloquer l’accès aux répertoires de sortie (`docs/`, `data/cache*.json`) si exposition Web.

## Tests & mises à jour
- Lancer la suite de tests : `PYTHONPATH=. pytest`
- Mettre à jour les dépendances via `pip install -r requirements.txt` si besoin.
- Recette avant prod : exécuter `python3 main.py --config config/conf.yaml --no-ai-report` sur un environnement de staging, puis vérifier les rapports générés.
- Smoke test : `PYTHONPATH=. python scripts/smoke.py` (http client + e2e report minimal).
- Packaging : `make package` génère `dist/cti-scraper.tar.gz` (archive du repo).

## Troubleshooting rapide
- Erreur robots : activer/désactiver `respect_robots` ou ajuster `allow_domains`.
- Taille max (`max_bytes`) dépassée : augmenter la limite dans `network.yaml` ou l’override de la source.
- Rapport IA : vérifier la commande (`ollama`, `llama`…) ou désactiver via `--no-ai-report`.
- Chemins manquants : vérifier `detail_dir`, `output.file`, `prompt_path` (le validateur remonte les erreurs).

## Docker / Compose (run rapide)
- Build & run (scraper + métriques HTTP) :
  ```bash
  docker compose up --build
  ```
  Le scraper tourne avec la config par défaut, sans IA. Les métriques sont exposées sur `http://localhost:9000/metrics` et `/health`.
- Volumes montés : `config/`, `data/`, `logs/`, `reports/`, `docs/` pour modifier/inspecter facilement.
- Activer l’IA : modifiez `docker-compose.yml` (retirez `--no-ai-report` de la commande) et assurez-vous que la commande IA est disponible dans l’image.
- Ressources : ajustez les limites CPU/RAM via la section `deploy` (commentée).
- Services additionnels :
  - `mongo` : base MongoDB pour le cache/résultats (config via `MONGO_URI` ou Vault).
  - `vault` : Vault dev (sans secrets par défaut), à configurer via env `VAULT_ADDR`/`VAULT_TOKEN` et un secret KV v2 (`VAULT_SECRET_PATH`).
