# Contexte architecture

- Racine du snapshot : `/home/noxe/projet/cti/Intelium`
- Fichiers scannés   : 142

## Langages dominants
- python · 97 fichiers (ex: requirements/app/cti_core/Source.py, requirements/app/cti_core/__init__.py, requirements/app/cti_core/cli.py)
- yaml · 13 fichiers (ex: docker-compose.yml, requirements/app/.github/workflows/ci.yml, requirements/app/config/auth.yaml)
- markdown · 7 fichiers (ex: requirements/app/.pytest_cache/README.md, requirements/app/Readme.md, requirements/app/docs/CONFIG.md)
- json · 4 fichiers (ex: requirements/app/data/health.json, requirements/app/data/keyword.json, requirements/app/data/sandbox/docs/api/CISA-KEV.json)
- html · 3 fichiers (ex: requirements/app/data/sandbox/docs/html/CERT-FR-d1-d2.html, requirements/app/data/sandbox/docs/html/CERT-FR-d1.html, requirements/app/data/sandbox/docs/html/CERT-FR.html)

## Signaux frameworks/outillage
- python · pip-requirements (requirements/app/requirements.txt)

## Architecture logique
- Pipeline : scan → map → analyze
  - scan : construit un snapshot (arbre de fichiers + README).
  - map  : agent analyste (langages, frameworks, docs, entrypoints, watchers) et génère `architecture.md`.
  - analyze : agent chef de projet (priorités, décisions) sur snapshot + changelog.

## Composants clés
- (composants non identifiés)

## Données échangées
- Snapshot : {root, tree[], readmes[]} issu de `scan`.
- architecture.md : mémo généré par l’agent analyste (ce fichier).
- Changelog (optionnel) : JSON passé à `analyze`.

## Points d’entrée probables
- requirements/app/cti_core/cli.py
- requirements/app/main.py
- requirements/app/tools/http/client.py

## Documentation repérée
- README : requirements/app/Readme.md · 🛡️ Agent IA CTI – Scraper + Analyse + CI/CD
- README : requirements/app/.pytest_cache/README.md · pytest cache directory #
- Doc : requirements/app/data/sandbox/docs/api/CISA-KEV.json
- Doc : requirements/app/data/sandbox/docs/html/CERT-FR-d1-d2.html
- Doc : requirements/app/data/sandbox/docs/html/CERT-FR-d1.html
- Doc : requirements/app/data/sandbox/docs/html/CERT-FR.html
- Doc : requirements/app/data/sandbox/docs/xml/CERT-FR-RSS.xml
- Doc : requirements/app/data/sandbox/docs/xml/EXPLOIT-DB-RSS.xml
- Doc : requirements/app/data/sandbox/docs/xml/HACKER-NEWS-RSS.xml
- Doc : requirements/app/data/sandbox/docs/xml/MS-SECURITY-BLOG.xml
- Doc : requirements/app/data/sandbox/docs/xml/NCSC-RSS.xml
- Doc : requirements/app/data/sandbox/docs/xml/SECURELIST-RSS.xml

## Watchers / boucles rapides
- pytest (quick): `pytest -q`

## IA / Providers
- Modes : `model` (API) ou `client_ia` (clients locaux).
- Sélection : auto-préférence Codex si présent, sinon `--ia-provider` ou `/provider` dans le shell.

## Agents Carabiner
- Analyste : cartographie langages/frameworks/docs/entrypoints, génère `architecture.md`.
- Tests : propose commandes de tests et pistes de couverture (sortie `tests` dans le bundle).
- Chef de projet : priorités/décisions à partir du snapshot et du changelog.

## Commandes CLI utiles
- `carabiner` (shell interactif `/`), `carabiner map <path> --ia-mode ...`, `carabiner full ...`.
- Flags : `--ia-mode`, `--ia-provider`, `-i` (prompts), `-H` (résumé humain).


> Généré automatiquement par l’agent analyste (snapshot-only).