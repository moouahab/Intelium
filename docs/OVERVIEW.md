# CTI Scraper – Guide rapide

## Architecture
- `main.py` : point d’entrée, appelle `cti_core.runner.run()`.
- `cti_core/runner.py` : charge la config, construit le cache, lance le `Scraper`, sort un résumé JSON.
- `cti_core/config_model.py` : lecture config (includes), keywords, sources, policies (`network`, `crawler`), storage target.
- `cti_core/scraper.py` : crawl/download, respect cache, collecte des résultats. `CrawlerState` (cti_core/crawler_state.py) gère queue/visited. Respect robots.txt (optionnel) + délai crawl configurables. La logique cache/résultats est centralisée dans `cti_core/result_recorder.py`. La création d’enfants HTML et la normalisation des overrides passent par `cti_core/sources_factory.py`.
- `tools/download.py` : handlers par type (html/api/xml/pdf/csv/txt/image/ignore) avec streaming, limites, stockage sous `docs/<type>/...`.
- `tools/report.py` : génération de rapport (markdown/json), découpe par source si configuré. `tools/ai_report.py` (optionnel) permet de générer un rapport CTI via un LLM local en CLI.
- Utilitaires : `tools/http/` (network + request_context + policies + URL utils + url_policy + auth headers par domaine), `tools/html_links.py` (extraction liens), `tools/cache.py` + `cache_factory.py` (cache global ou par site), `tools/logger_utils.py` (logging).
- Configs : `config/conf.yaml` inclut `sources.yaml`, `network.yaml`, `crawler.yaml`, `scraping.yaml`, etc.

## Flux d’exécution
1. Lecture config (`ConfigModel`) + keywords + policies réseau/crawler.
2. Choix du cache (global ou par site selon `cache.per_site`).
3. `Scraper.run()` parcourt les sources, respecte le cache, télécharge, suit les liens HTML jusqu’à `crawler.max_depth` / `crawler.max_pages`, en restant sur le domaine si `same_domain_only`.
4. Chaque résultat est enregistré dans le cache et remonté dans un résumé JSON affiché en fin de run.

## Commandes utiles
- Lancer le scrape : `python3 main.py`
- Tests : `python3 -m pytest -q`
- Options courantes (CLI de `main.py`) :
  - `--config config/conf.yaml` : chemin de la config
  - `--no-ai-report` / `--ai-report` : forcer ou désactiver le rapport IA

## Ajouter une source avec overrides/auth
- Dans `config/sources.yaml`, ajouter un bloc :
  ```yaml
  - name: cert-fr
    url: https://www.cert.ssi.gouv.fr/alerte/
    type: html
    overrides:
      max_bytes: 1048576
      respect_robots: false
      crawl_delay_seconds: 1
  ```
- Dans `config/auth.yaml`, section `authentication` :
  ```yaml
  authentication:
    headers:
      User-Agent: "CTI-Scraper"
    hosts:
      api.example.com:
        Authorization: "Bearer <token>"
  ```

## Activer le rapport IA local
- Dans `config/output.yaml` :
  ```yaml
  output:
    ai_report:
      enabled: true
      command: "ollama run llama3"   # ou autre binaire local (llama.cpp, etc.)
      output: reports/ai_report.md
      timeout: 120
      prompt_template: |
        Tu es un analyste CTI. Résume et synthétise :
        {results_json}
      prompt_path: ""                 # optionnel, pour lire un template depuis un fichier
  ```
- Dans `config/prompt.yaml`, vous pouvez définir un template réutilisable, puis le référencer via `output.ai_report.prompt_path`.
  ```
- Le modèle est appelé en CLI locale (pas d’accès réseau). Le prompt peut être ajusté via `prompt_template` (`{results_json}` est remplacé par les données).

## Configs clés
- `config/sources.yaml` : sources CTI (CERT-FR, CISA KEV, RSS Talos/NCSC/HackerNews/SecurityWeek, CVE sample, OTX).
- `config/network.yaml` : HTTPS, block_private, allow_domains, max_bytes, timeout, dossier de sauvegarde. Garde-fous : enforce_https + blocage réseau privé, allowlist stricte, robots.txt respecté par défaut.
- `config/crawler.yaml` : `max_depth`, `max_pages`, `same_domain_only`, `allow_domains` (fallback sur réseau), `respect_robots`, `crawl_delay_seconds`, `max_concurrent`.
- `config/scraping.yaml` : règles d’extraction par type (HTML tags, API JSONPath, XML tags, PDF/CSV/image/TXT options).
- `config/cache.yaml` : fichier cache, auto_save, `per_site` (fichiers par domaine).
- `config/logging.yaml` : niveau, fichier log (rotation), console.
- `config/output.yaml` : format rapport, chemin principal, split_per_source/detail_dir, langue. Bloc `ai_report` activé par défaut en mode LangGraph : `mode`, `langgraph_llm_command` (ex: `codex exec --skip-git-repo-check` ou autre CLI locale), `command` (fallback CLI), `output`, `timeout`, `prompt_template` (texte où `{results_json}` est remplacé par les données) ou `prompt_path` pour lire un template depuis un fichier, `pass_prompt_as_arg` et `prompt_via_file` (pour passer le prompt via stdin/fichier). Auto-détection couvre : ollama, llama/llama.cpp, codex, copilot, code.
- Overrides par source (via `sources.yaml`) : bloc `overrides` pour `max_bytes`, `respect_robots`, `crawl_delay_seconds` (voir normalisation dans `sources_factory.normalize_overrides`).
- Normalisation URL : `crawler.url_normalizer` (`strip` par défaut, options `lower`, `strip-lower`).

## auth.yaml (options)
- `authentication.headers` : headers globaux (ex: User-Agent), support `${ENV_VAR}` (headers sensibles masqués dans les logs)
- `authentication.hosts.<domaine>` : headers spécifiques (ex: Authorization), support `${ENV_VAR}` (headers sensibles masqués dans les logs)

## output.ai_report (options)
- `enabled` : activer/désactiver
- `command` : ex `ollama run llama3` (auto-détecté si vide)
- `output` : chemin du rapport IA
- `timeout` : délai max de génération
- `prompt_template` : prompt inline (utilise `{results_json}`)
- `prompt_path` : chemin d’un template de prompt

## Points d’attention
- Réseau : si accès restreint, tester avec des mocks ou fichiers locaux.
- Taille : `max_bytes` coupe les gros flux (ex. CISA KEV) → augmenter si besoin.
- Auth : renseigner les clés dans `config/auth.yaml` via variables d’environnement (ne pas committer les secrets).

## Résumé JSON de fin de run
Affiché par `runner.py`, format :
```json
{
  "sources": [
    {"url": "...", "name": "...", "type": "html", "status": "downloaded|error|skipped-cache", "error": null, "saved_path": "docs/html/..."}
  ]
}
```
