# 🛡️ Intelium – Agent CTI (Scraper + Analyse IA + Observabilité)

Ce dépôt orchestre un agent CTI capable de collecter des sources (CERT/RSS/API/PDF/Images), d’analyser et de scorer les résultats, et de produire des rapports (Markdown/JSON/IA). Il embarque une stack Docker (scraper, IA CLI, métriques, Mongo, Vault, Prometheus, Grafana).

## Structure rapide
- `Makefile` : cibles `run`, `test`, `build`, `init-vault`… (voir plus bas).
- `srcs/docker-compose.yml` : services scraper/metrics/mongo/vault/prometheus/grafana.
- `srcs/requirements/app/` : code Python (scraper, parseurs, config, scripts IA, tests).
- `srcs/requirements/vault/scripts/init_vault.sh` : init + unseal Vault (dev).
- `docs/` et `srcs/requirements/app/docs/` : guides d’archi, parsing, déploiement, sécurité, runbook, DevSecOps.

## Fonctionnement
1) `main.py` lit `config/conf.yaml` et inclut le reste (`network.yaml`, `crawler.yaml`, `sources.yaml`, `scraping.yaml`, `output.yaml`, `auth.yaml`, etc.).
2) `cti_core/scraper.py` télécharge chaque source (BFS configurable), respecte robots/délais/allowlist, stocke sous `docs/<type>/...`, calcule un hash/cache, et passe le contenu aux parseurs.
3) `tools/parsing/parser.py` route vers les parseurs (HTML/API/XML/CSV/TXT/PDF/OCR) avec options par type et par source, extraction IOC et sanitation optionnelles.
4) `tools/report.py` génère les rapports Markdown/JSON, `tools/ai_report.py` peut appeler un LLM local (Mistral via CLI par défaut) pour synthèse CTI.
5) Résumé JSON affiché en fin de run (statut, chemin sauvegardé, extraits).
6) Quotas globaux optionnels (`crawler.global_max_pages/max_total_bytes`) pour couper un run trop volumineux ; les sources restantes sont marquées `skipped-quota`.
7) Parseur CERT/KEV contextuel : si le nom de source contient `cert`/`kev`/`cisa` (ou si `certkev: true` est activé dans `scraping.yaml`), le scraper extrait les CVE/CERTFR avec un extrait de contexte en plus des balises classiques.

## Dépendances
- Python 3.10+, packages `pip install -r srcs/requirements/app/requirements.txt`.
- Tesseract + langues installées si OCR utilisé (pytesseract/Pillow déjà dans `requirements.txt`).
- pdfplumber pour PDF (déjà dans `requirements.txt`).
- Docker/Compose pour la stack complète.

## Commandes clés (racine du repo)
- `make deps` : installe les deps Python (dans `srcs/requirements/app`).
- `make test` : lance `python3 -m pytest -q`.
- `make run` : démarre la stack docker (scraper, métriques, mongo, vault…).
- `make logs` : suit les logs principaux.
- `make restart` : restart scraper + métriques.
- `make init-vault` : initialise/unseal Vault via `srcs/requirements/vault/scripts/init_vault.sh`.

## Préparer l’environnement (.env)
```bash
cp .env.example .env
# puis compléter les valeurs réelles (MISTRAL_API_KEY, MONGO_URI, SLACK_WEBHOOK_URL, SMTP_*)
```
Le `Makefile` lance `docker compose` avec `--env-file .env` pour garantir l’injection des variables.

## Usage rapide (hors Docker)
```bash
cd srcs/requirements/app
python3 main.py --config config/conf.yaml           # lance le scrape
python3 -m pytest -q                                # tests
```

## Configuration (principaux fichiers sous `srcs/requirements/app/config/`)
- `conf.yaml` : inclut tous les autres YAML.
- `sources.yaml` : liste des sources CTI (type html/api/xml/pdf/image/txt/csv, overrides).
- `network.yaml` : HTTPS forcé, block_private, allowlist, max_bytes, sandbox, scan YARA/AV optionnel.
- `crawler.yaml` : profondeur/pages max, respect robots, délai crawl, same_domain_only.
- `scraping.yaml` : règles de parsing par type (tags HTML, JSONPath API, tags XML, OCR/PDF).
- `output.yaml` : rapport Markdown/JSON, split par source, options IA (commande, timeout, prompt).
- `ops.yaml` : pré‑checks d’environnement (strict_env, alerting vars, secrets requis).
- `auth.yaml` : headers globaux + par host, valeurs injectables via env (`${ENV_VAR}`).
- `prompt.yaml` : templates de prompt IA réutilisables.
- `cache.yaml` : backend fichier ou Mongo. Avec `backend: mongo` + `MONGO_URI`, le cache et les résultats (extraits/keywords/saved_path, y compris issus du cache) sont persistés dans Mongo.

## IA (Mistral CLI)
- Script conseillé : `python scripts/mistral_llm.py` (clé `MISTRAL_API_KEY`, modèle `MISTRAL_MODEL`).
- `output.ai_report.enabled: true` pour activer la synthèse IA. Le prompt peut venir de `output.ai_report.prompt_template` ou `prompt_path`.
- Fallback LangGraph (local) possible via `mode: langgraph` si configuré.
- Fallback local rapide/gratuit : `scripts/ollama_llm.py` (Ollama). Configure `OLLAMA_MODEL` dans `.env` (ex: `llama3.2:3b` pour vitesse) et ajuste `OLLAMA_NUM_CTX`/`OLLAMA_NUM_PREDICT` pour limiter la latence.
- En Docker, renseigne aussi `OLLAMA_HOST=http://host.docker.internal:11434` (ou l’URL de ton service Ollama) pour que le conteneur accède à Ollama.

## Parseurs et options
- HTML : tags/CSS/XPath, `include_attributes`, sanitation optionnelle.
- API/JSON : JSONPath (`jsonpath-ng` si dispo, fallback simple), extraction CVSS si présent.
- XML : tags listés, sanitation optionnelle.
- CSV : delimiter, header, colonnes.
- TXT : texte brut + IOC.
- PDF : pdfplumber, `max_pages`, `max_chars`, `keep_images`, `extract_text`.
- Image : OCR Tesseract, `languages`, `max_chars`, `ocr: true/false`.
- Extraction IOC (CVE/URL/IP) activable par type/sources.

## Observabilité et stockage
- Métriques exposées par `scripts/metrics_server.py` (Prometheus scrappé via `srcs/prometheus.yml`).
- Grafana (port 3000, admin/admin par défaut à changer). Prometheus charge les règles d’alerte depuis `srcs/prometheus_rules.yml` (ex : taux d’échec fetch/run, endpoint métriques down, quota atteint) et envoie vers Alertmanager.
- Alertmanager (port 9093) : configuration injectée via `srcs/docker-compose.yml` (bloc `configs`) avec les variables `${...}`. Assure‑toi que `SLACK_WEBHOOK_URL` et les variables SMTP ne sont pas vides, sinon Alertmanager refuse la config.
- Dashboard “CTI - Overview” inclut un bloc santé (quota, top raisons, statuts). Les alertes exploitent les labels `severity` définis dans `prometheus_rules.yml` (warning/critical/info).
- Mongo optionnel pour cache + résultats : définir `MONGO_URI` (env/Vault) et laisser `backend: mongo` dans `config/cache.yaml`.
- Logs/rapports écrits sous `srcs/requirements/app/logs/` et `.../reports/` (ignorés par Git).
- Admin cache : `python scripts/cache_admin.py --stats/--clear --file data/cache.json` ou `--mongo-uri ... --db cti --collection cache`.
- Grafana : dashboard par défaut provisionné (CTI - Overview) via `srcs/grafana/` (datasource Prometheus auto, panels fetch/runs/erreurs/reasons). Port 3000 (admin/admin par défaut).

## Vault (dev)
- `make init-vault` → lance `srcs/requirements/vault/scripts/init_vault.sh` : init + unseal (1 clé), affiche `VAULT_TOKEN` et `UNSEAL_KEY`.
- Ajoute `VAULT_TOKEN` (et `VAULT_ADDR` si besoin) dans `.env` pour le scraper. Ne pas committer l’UNSEAL_KEY.

## Exemples
- Ajouter une source HTML avec overrides :
  ```yaml
  # config/sources.yaml
  - name: cert-fr
    url: https://www.cert.ssi.gouv.fr/alerte/
    type: html
    overrides:
      respect_robots: false
      crawl_delay_seconds: 1
      max_bytes: 1048576
  ```
- Activer rapport IA Mistral :
  ```yaml
  # config/output.yaml
  output:
    ai_report:
      enabled: true
      command: "python scripts/mistral_llm.py"
      output: reports/ai_report.md
      timeout: 120
      prompt_template: |
        Tu es un analyste CTI. Résume les menaces clés :
        {results_json}
  ```
- OCR en français/anglais avec limites :
  ```yaml
  # config/scraping.yaml
  data_scraper:
    image:
      ocr: true
      languages: ["eng", "fra"]
      max_chars: 2000
  ```

## Sécurité et bonnes pratiques
- Garder `network.enforce_https` + `block_private` actifs et restreindre `allow_domains`.
- Ne pas committer de secrets (.env déjà ignoré). Utiliser `${ENV_VAR}` dans `auth.yaml`.
- Activer `scan_command` (YARA/AV) si vous consommez des artefacts non fiables.
- Ajuster `max_bytes`/`max_pages`/`max_chars` pour éviter les payloads trop gros.

## Tests et qualité
- `python3 -m pytest -q` : couverture sur config, download, cache, parseurs (y compris PDF/OCR), AI pipeline, crypto. Installez les deps dev avec `pip install -r srcs/requirements/app/requirements-dev.txt` pour inclure les mocks Mongo.
- Ajouter des tests spécifiques via `srcs/requirements/app/tests/`.
- CI : workflow GitHub Actions (`.github/workflows/ci.yml`) exécute l’installation des deps et la suite pytest sur Python 3.10.

## Déploiement (docker)
```bash
make run                         # build + up stack
docker logs -f cti-scraper       # logs scraper
docker compose -f srcs/docker-compose.yml restart cti-scraper codex metrics
```
Voir `srcs/requirements/app/docs/DEPLOY.md` pour systemd et rotation de logs.
