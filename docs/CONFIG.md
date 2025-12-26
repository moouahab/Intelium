# Configuration et tuning

## Fichiers clés
- `config/conf.yaml` : point d’entrée, inclut les autres YAML.
- `config/sources.yaml` : liste des sources, type (html/api/xml…) et overrides spécifiques.
- `config/network.yaml` : garde-fous réseau (HTTPS, block_private, allowlist, max_bytes, sandbox, scan, metrics_path).
- `config/crawler.yaml` : profondeur, limites de pages, robots/délai, parallélisme (`max_concurrent`).
- `config/scraping.yaml` : règles d’extraction par type, sanitation, IOC.
- `config/output.yaml` : rapport (format, split, AI report + scoring).
- `config/auth.yaml` : entêtes globaux et par domaine (supports `${ENV_VAR}`).

## Réseau / garde-fous (`config/network.yaml`)
- `enforce_https` : bloque le HTTP.
- `block_private` : bloque IP privées (y compris via résolution DNS).
- `allow_domains` : liste blanche. Ajoutez ici tout nouveau domaine cible.
- `max_bytes` : coupe les téléchargements trop volumineux.
- `scanner` / `scan_command` : YARA/AV optionnel.
- `sandbox_dir` : confinement des écritures.
- `metrics_path` : fichier `health.json` pour tracer succès/erreurs/durée des fetch.

## Crawler (`config/crawler.yaml`)
- `max_depth` / `max_pages` : bornes du crawl.
- `same_domain_only` : reste sur le domaine (recommandé).
- `allow_domains` : override de l’allowlist réseau.
- `respect_robots` + `crawl_delay_seconds` : respect des robots.txt et délais.
- `max_concurrent` : parallélisme (2 par défaut, thread-safe côté cache/UA/proxy).
- `user_agent`, `retry_attempts`, `retry_backoff_seconds` : tuning HTTP client.

## Scraping (`config/scraping.yaml`)
- Règles par type (extract tags/css/xpath, CSV delimiter, OCR/PDF, sanitize).
- `extract_iocs`: active l’extraction CVE/URL/IP dans les extraits.
- `per_source` : permet d’overrider les règles pour une source donnée.
- Parsers extensibles : via `ParserRegistry` si besoin d’ajouter un type.

## Sortie / Rapport (`config/output.yaml`)
- `format` : `markdown` ou `json`, `file` : chemin principal, `split_per_source` + `detail_dir`.
- AI report (`ai_report`) :
  - `enabled`, `command` (ou auto-détection), `prompt_template`/`prompt_path`, `timeout`.
  - `analysis` : étape IA intermédiaire optionnelle (prompt dédié).
  - `scoring` : poids configurables (malware/vulnerability/attack_technique/default) et CVSS (seuils high/medium). Priorité “high” forcée si malware + CVE.
- Logging : `config/logging.yaml` (niveau, fichier, rotation).

## Auth (`config/auth.yaml`)
- `authentication.headers` : entêtes globaux (User-Agent…).
- `authentication.hosts.<domaine>` : entêtes par domaine (token, API key). Utiliser `${ENV_VAR}` pour injecter les secrets.

## Mode headless
- Pour les pages JS/infinite scroll : activer `overrides.headless: true` sur une source. La stratégie headless est extensible ; Playwright est utilisée si présente, sinon Selenium si installé. Vous pouvez injecter une autre stratégie via le code (Selenium/Playwright custom) sans changer la config.

## Overrides par source (`config/sources.yaml`)
- `overrides.max_bytes`, `respect_robots`, `crawl_delay_seconds`, `headers`, `user_agent`, `headless`.
- Les overrides sont normalisés et transmis au client HTTP et au policy réseau.

## Métriques et santé
- `data/health.json` : enrichi par l’orchestrateur (runs) et par les fetch individuels (si `metrics_path` configuré). Contient compteurs succès/échec et somme des durées de fetch.
- `scripts/orchestrator.py` : lance le scraper périodiquement avec enregistrement des métriques.
