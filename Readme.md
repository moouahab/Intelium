# 🛡️ Agent IA CTI – Scraper + Analyse + CI/CD

#### 🎯 Objectif

Créer un agent intelligent capable de :

    Scraper automatiquement des sites web CTI (ou généraux)
    Analyser les contenus avec un moteur IA (LangGraph + LLM)
    Extraire des données utiles : texte, images, menaces, vulnérabilités
    Filtrer les infos grâce à une base de mots-clés (keywords.json)
    Construire automatiquement des tests
    Intégrer un pipeline CI/CD : push seulement si tout est valide

---

###  📁 Structure du projet

```bash
.
├── Readme.md         # 📝 Présentation du projet
├── cti_core/         # 🧱 ConfigModel, Source, future orchestration
├── config/           # ⚙️ Config YAML + mots-clés JSON
│   ├── conf.yaml
│   ├── network.yaml
│   ├── crawler.yaml
│   └── keyword.json
├── docs/             # 📚 Doc future ou screenshots, API, etc.
│   ├── OVERVIEW.md   # 🧭 Guide rapide (archi, flux, configs clés)
│   └── PARSING.md    # 📄 Détails extraction/parsing et rapport
├── main.py           # 🚀 Point d’entrée du projet
└── tests/            # ✅ Tests unitaires plus tard
```
---

## ⚙️ Fonctionnement (aperçu)

1. Lecture de la config modulaire (`conf.yaml` + `include` des autres YAML).
2. Chargement de la librairie de mots-clés (`data/keyword.json` avec fallback en cas de typo).
3. Normalisation des sources (types supportés : html, api, xml, pdf, csv, txt, image, ignore).
4. Téléchargement via `Source.download_manager` / `tools/download.py` et crawl :
   - garde-fous réseau : HTTPS forcé, block_private, allowlist de domaines, limite de taille (`network.yaml`).
   - crawl (BFS) configurable (`crawler.yaml`) : profondeur/max pages, même domaine only, allowlist.
   - stockage : contenu écrit sous `docs/<type>/<nom_source>_<hôte>.ext`.
   - hash pour détecter les changements.
5. Filtrage/IA/rapport (à implémenter) puis CI/CD (à venir).

## 🔧 Pré-requis
- Python 3.10+
- Dépendances : `requests`, `PyYAML`, `cryptography`, `pytest`
  ```bash
  pip install requests PyYAML cryptography pytest
  ```

## 🚀 Utilisation rapide / CLI
- Lancer le scrape : `python3 main.py`
- Options CLI :
  - `--config config/conf.yaml` : chemin de la config
  - `--ai-report` / `--no-ai-report` : forcer ou désactiver le rapport IA (sinon dépend de `output.ai_report.enabled`)
- Configs clés :
  - `config/conf.yaml` inclut `sources.yaml`, `scraping.yaml`, etc.
  - `config/network.yaml` : HTTPS, block_private, allowlist, max_bytes, dossier de sauvegarde.
  - `config/crawler.yaml` : profondeur, max pages, same_domain_only, allow_domains, respect_robots, crawl_delay_seconds, max_concurrent, url_normalizer.
  - `config/auth.yaml` : headers globaux + `hosts` par domaine (ne pas committer les secrets).
  - `config/output.yaml` : rapport markdown/json, split, IA (`ai_report` activé par défaut, commande auto-détectée si vide, prompt_template ou prompt_path).
  - `config/prompt.yaml` : template de prompt IA réutilisable.

## 🔐 Chiffrement (tools/crypter.py)
- Hachage : `compute_sha256(path)`, `compute_sha256_from_text(str)`, `verify_file_integrity(path, hash)`.
- Clés : `generate_key()` (aléatoire AES 128/192/256) ou `derive_key_from_password("motdepasse")` (scrypt).
- Chiffrement authentifié : `encrypt_file(path, key, associated_data=None)` produit `*.enc` (nonce + ciphertext + tag GCM).
- Déchiffrement : `decrypt_file(enc_path, key, associated_data=None)` vérifie le tag et restaure le contenu. Lève une erreur si la clé est mauvaise ou le fichier corrompu.

## ✅ Tests
- Lancer la suite :
  ```bash
  python3 -m pytest -q
  ```
- Tests existants : config modulaire + keywords, téléchargement multi-format, Source/download_manager, crypto (hash, intégrité, chiffrement/déchiffrement AES-GCM).

## 🛠️ Déploiement & supervision
- Voir `docs/DEPLOY.md` pour un exemple systemd, la gestion des logs/rotation et la supervision.

---
