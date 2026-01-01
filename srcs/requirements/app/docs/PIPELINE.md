# Pipeline CTI – déploiement et fonctionnement

## Objectif
Collecter des sources CTI (CERT-FR, KEV, RSS, OTX, etc.), appliquer un scoring/IA (Mistral), stocker/cache dans Mongo, tracer les runs (Prometheus/Grafana), avec des garde-fous réseau et des secrets gérés par env/Vault.

## Services Docker Compose
- **cti-scraper** : orchestrateur + scraper Python, rapports Markdown/JSON sous `reports/`.
- **metrics** : expose `/metrics` et `/health` (fichier `data/health.json`).
- **mongo** : cache persistant (si `MONGO_URI` défini).
- **vault** : mode dev (token/unseal dans les logs). À sécuriser pour la prod.
- **codex** : conteneur utilitaire pour exécuter les commandes IA/CLI.
- **prometheus** : scrape `metrics:9000`.
- **grafana** : dashboards provisionnés (datasource Prometheus auto).
- **alertmanager** : alertes (Slack/SMTP) alimentées par Prometheus.

## Secrets et .env (à ne pas commiter)
Utiliser `.env.example` comme base puis créer `.env`. Exemple de clés à fournir :
```
OTX_API_KEY=...
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-large-latest
MONGO_URI=mongodb://cti-mongo:27017/cti
VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=...  # si utilisé
SLACK_WEBHOOK_URL=...
ALERT_EMAIL_TO=...
ALERT_EMAIL_FROM=...
SMTP_HOST=...
SMTP_PORT=...
SMTP_USER=...
SMTP_PASS=...
```
Le fichier `.env` est lu par `env_file` dans compose (et `make run` passe `--env-file .env`). Ne pas versionner les valeurs réelles.

## IA (Mistral) et rapport
- Commande IA : `python scripts/mistral_llm.py` (clé `MISTRAL_API_KEY` requise).
- Rapport IA et principal fusionnés dans `reports/rapport.md` (format markdown + export JSON).
- Pour éviter les prompts trop gros : limites `max_results`, `max_extracted_per_source`, `max_extracted_chars` dans `config/output.yaml`.
- Fallback local rapide/gratuit : `python scripts/ollama_llm.py` (Ollama). Configurer `OLLAMA_MODEL`/`OLLAMA_TIMEOUT`/`OLLAMA_RETRIES` et, pour la vitesse, `OLLAMA_NUM_CTX`/`OLLAMA_NUM_PREDICT` dans `.env`.
- En Docker, ajouter `OLLAMA_HOST=http://host.docker.internal:11434` (ou l’URL de ton service Ollama).

## Garde-fous / réseau
- `config/network.yaml` : HTTPS forcé, blocage IP privées, allowlist stricte, sandbox `/tmp/cti-sandbox`, scan YARA (yara installé dans l’image).
- `config/crawler.yaml` : profondeur/pages bornées, respect robots, délais.

## Observabilité
- `metrics` → Prometheus (`srcs/prometheus.yml`), Grafana sur `http://localhost:3000`.
- Alertes → Alertmanager (`http://localhost:9093`) avec Slack/SMTP si configuré.
- Fichier santé : `srcs/requirements/app/data/health.json`.
- Logs : `srcs/requirements/app/logs/`.

## Commandes clés
- Démarrer/relancer : `make run` (ou `docker compose --env-file .env -f srcs/docker-compose.yml up -d --build`).
- Logs scraper : `docker logs -f cti-scraper`.
- Rebuild scraper/IA/metrics après changement code : `docker compose -f srcs/docker-compose.yml build cti-scraper codex metrics`.
- Run manuel avec IA : `docker exec -it cti-scraper python main.py --config config/conf.yaml --ai-report`.

## Vault (dev)
- En mode dev, le root token et l’unseal key apparaissent dans les logs (`docker logs cti-vault | grep 'Root Token'`).
- Pour repartir propre : `docker compose -f srcs/docker-compose.yml down && rm -rf srcs/requirements/app/vault/* && make run` puis `make init-vault`.
- En prod, utiliser un mode Vault non-dev, token hors Git, et montages sécurisés.

## Points de sécurité
- Ne pas élargir l’allowlist ou désactiver `block_private` sans autorisation.
- Ne pas committer `.env` avec des clés réelles.
- Scanner YARA actif : `config/network.yaml` (l’exécutable est dans l’image).
- Mongo sans auth par défaut : activer l’auth si exposé ou en environnement partagé.
