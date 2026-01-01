# Configuration et tuning

## Sommaire
- [Fichiers clés](#fichiers-clés)
- [Réseau / garde-fous](#réseau--garde-fous-confignetworkyaml)
- [Crawler](#crawler-configcrawleryaml)
- [Scraping](#scraping-configscrapingyaml)
- [Sortie / Rapport](#sortie--rapport-configoutputyaml)
- [Auth](#auth-configauthyaml)
- [Mode headless](#mode-headless)
- [Overrides par source](#overrides-par-source-configsourcesyaml)
- [Métriques et santé](#métriques-et-santé)
- [Getting started](#getting-started)

## Fichiers clés
- `config/conf.yaml` : point d’entrée, inclut les autres YAML.
- `config/sources.yaml` : liste des sources, type (html/api/xml…) et overrides spécifiques.
- `config/network.yaml` : garde-fous réseau (HTTPS, block_private, allowlist, max_bytes, sandbox, scan, metrics_path).
- `config/crawler.yaml` : profondeur, limites de pages, robots/délai, parallélisme (`max_concurrent`).
- `config/scraping.yaml` : règles d’extraction par type, sanitation, IOC.
- `config/output.yaml` : rapport (format, split, AI report + scoring).
- `config/auth.yaml` : entêtes globaux et par domaine (supports `${ENV_VAR}`).
- `config/ops.yaml` : pré‑checks d’environnement (strict_env, vars requises).

## Réseau / garde-fous (`config/network.yaml`)
- `enforce_https` : bloque le HTTP.
- `block_private` : bloque IP privées (y compris via résolution DNS).
- `offline` : mode cache-only (aucun fetch réseau ; si pas de cache, statut `offline`).
- `allow_domains` : liste blanche. Ajoutez ici tout nouveau domaine cible.
- `max_bytes` : coupe les téléchargements trop volumineux.
- `scanner` / `scan_command` : YARA/AV optionnel.
- `sandbox_dir` : confinement des écritures (recommandé).
- `metrics_path` : fichier `health.json` pour tracer succès/erreurs/durée des fetch.
- **Sécurité** : gardez `enforce_https` et `block_private` à true, ne desserrez l'allowlist que pour des cibles autorisées. Ne stockez pas de secrets dans ce fichier.

## Crawler (`config/crawler.yaml`)
- `max_depth` / `max_pages` : bornes du crawl par source.
- `global_max_pages` / `global_max_bytes` (alias `max_total_pages` / `max_total_bytes`) : quota global sur un run (toutes sources confondues). Si atteint, les sources restantes sont marquées `skipped-quota`.
- `same_domain_only` : reste sur le domaine (recommandé).
- `allow_domains` : override de l’allowlist réseau.
- `respect_robots` + `crawl_delay_seconds` : respect des robots.txt et délais.
- `max_concurrent` : parallélisme (2 par défaut, thread-safe côté cache/UA/proxy).
- `user_agent`, `retry_attempts`, `retry_backoff_seconds` : tuning HTTP client.
- **Sécurité** : gardez des bornes strictes (depth/pages), respectez robots/délai, n’augmentez `max_concurrent` qu’après test. `same_domain_only` à true sauf besoin explicite.

## Scraping (`config/scraping.yaml`)
- Règles par type (extract tags/css/xpath, CSV delimiter, OCR/PDF, sanitize).
- `extract_iocs`: active l’extraction CVE/URL/IP dans les extraits.
- `per_source` : permet d’overrider les règles pour une source donnée.
- Parsers extensibles : via `ParserRegistry` si besoin d’ajouter un type.
- `certkev: true` (par type ou par source) active l’extraction contextuelle pour les bulletins CERT/KEV (repère les CVE/CERTFR dans le texte et garde un extrait court). Auto-activé pour les sources dont le nom contient `cert`, `kev` ou `cisa`.

## Sortie / Rapport (`config/output.yaml`)
- `format` : `markdown` ou `json`, `file` : chemin principal, `split_per_source` + `detail_dir`.
- `additional_formats` : liste optionnelle de formats supplémentaires à générer (ex: `["json"]`) en plus du format principal.
- `filter.vulnerability_only` : si true, filtre les résultats pour ne garder que les entrées avec vulnérabilité (keywords vulnérabilité ou CVE).
- AI report (`ai_report`) :
  - `enabled`, `command` (ou auto-détection), `prompt_template`/`prompt_path`, `timeout`.
  - `analysis` : étape IA intermédiaire optionnelle (prompt dédié).
  - `scoring` : poids configurables (malware/vulnerability/attack_technique/default) + `per_type` (poids par type) et CVSS (seuils high/medium). Priorité “high” forcée si malware + CVE.
  - `filter.vulnerability_only` : filtre côté IA pour ne garder que les entrées vulnérabilité (keywords vulnérabilité ou CVE).
- Logging : `config/logging.yaml` (niveau, fichier, rotation).

## Auth (`config/auth.yaml`)
- `authentication.headers` : entêtes globaux (User-Agent…).
- `authentication.hosts.<domaine>` : entêtes par domaine (token, API key). Utiliser `${ENV_VAR}` pour injecter les secrets.
- **Sécurité** : ne commitez jamais de secrets ; utilisez des variables d’environnement ou un vault. Limitez les entêtes aux domaines explicitement autorisés.

## Ops (`config/ops.yaml`)
- `strict_env` : si true, bloque le run si des variables requises sont manquantes.
- `require_auth_env` : vérifie que toutes les variables `${ENV_VAR}` dans `auth.yaml` sont présentes.
- `require_alerting_env` : vérifie les variables Slack/SMTP pour Alertmanager.
- `require_allowlist` : refuse un run si l’allowlist est vide (sécurité).
- `required_env` : liste supplémentaire à vérifier.

## Mode headless
- Pour les pages JS/infinite scroll : activer `overrides.headless: true` sur une source. La stratégie headless est extensible ; Playwright est utilisée si présente, sinon Selenium si installé. Vous pouvez injecter une autre stratégie via le code (Selenium/Playwright custom) sans changer la config.
- **Sécurité** : n’activez headless que sur des cibles autorisées ; conservez l’allowlist stricte.

## Overrides par source (`config/sources.yaml`)
- `overrides.max_bytes`, `respect_robots`, `crawl_delay_seconds`, `headers`, `user_agent`, `headless`.
- Les overrides sont normalisés et transmis au client HTTP et au policy réseau.
- **Sécurité** : ne relâchez pas les garde-fous (max_bytes, robots) sans besoin clair et accord explicite. Gardez `headless` désactivé par défaut.

## Métriques, stockage et santé
- `data/health.json` : enrichi par l’orchestrateur (runs) et par les fetch individuels (si `metrics_path` configuré). Contient compteurs succès/échec et somme des durées de fetch.
- `scripts/orchestrator.py` : lance le scraper périodiquement avec enregistrement des métriques.
- `scripts/health_summary.py` : résume `health.json` ou exporte en Prometheus (option `--prometheus`).
- `scripts/metrics_server.py` : expose `/metrics` (Prometheus) et `/health` (JSON) à partir de `health.json`.
- `scripts/cache_admin.py` : stats/purge du cache (fichier, per-site, ou Mongo). Utilise `--file`, `--dir`, ou `--mongo-uri` (fallback env/Vault `MONGO_URI`).
- **Sécurité/ops** : surveillez les logs et `health.json` pour détecter des échecs ou des domaines inattendus.
- Vault : un service Vault (dev) est présent dans docker-compose pour stocker des secrets ; aucune valeur n'est hardcodée, à configurer via variables d'environnement.
- Secrets : `MONGO_URI` (et autres) peuvent être injectés via env ou Vault (`VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_SECRET_PATH`; clé lue dans un secret KV v2).
- Mongo : service optionnel (compose) pour persister le cache **et** tous les résultats (y compris ceux issus du cache). Activez `backend: mongo` dans `config/cache.yaml` et fournissez `MONGO_URI` (env ou Vault). Les documents contiennent statut, extraits, mots-clés, saved_path.

## Getting started
1. Installer les dépendances : `make deps`
2. Lancer un run sans IA : `make run-no-ia`
3. Vérifier la santé : `python scripts/health_summary.py --file data/health.json`
