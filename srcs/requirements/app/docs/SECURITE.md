# Sécurité et conformité

## Sommaire
- [Périmètre autorisé](#périmètre-autorisé)
- [Limites et quotas](#limites-et-quotas)
- [Secrets et authentification](#secrets-et-authentification)
- [Stockage et sandbox](#stockage-et-sandbox)
- [IA et données](#ia-et-données)
- [Headless / JS](#headless--js)
- [Monitoring et traçabilité](#monitoring-et-traçabilité)
- [Ce qu’il ne faut pas faire](#ce-quil-ne-faut-pas-faire)

Ce scraper doit rester dans un périmètre autorisé et respectueux. Quelques règles pour éviter tout usage illégal ou abusif :

## Périmètre autorisé
- **Allowlist stricte** : n’ajoutez que des domaines explicitement autorisés dans `config/network.yaml` (`allow_domains`). Pas de wildcard.
- **Allowlist requise** : `ops.require_allowlist: true` bloque un run si l’allowlist est vide.
- **Block privé** : gardez `block_private: true` pour empêcher les accès réseaux internes/privés.
- **HTTPS** : conservez `enforce_https: true` pour éviter le HTTP en clair.
- **Robots/délais** : respectez `respect_robots: true` et un `crawl_delay_seconds` raisonnable.

## Limites et quotas
- **Bornes de crawl** : définissez `max_depth` et `max_pages` (crawler.yaml) pour éviter l’exploration massive.
- **Poids** : `max_bytes` limite la taille des téléchargements (network.yaml).
- **Parallélisme** : `max_concurrent` modéré (2 par défaut) pour ne pas surcharger les cibles ; augmentez seulement après tests contrôlés.

## Secrets et authentification
- Ne committez jamais de clés/tokens. Utilisez `${ENV_VAR}` dans `config/auth.yaml` et des variables d’environnement ou un vault.
- Limitez les entêtes au strict nécessaire pour les domaines autorisés.

## Stockage et sandbox
- **Sandbox** : conservez un `sandbox_dir` pour confiner les écritures (network.yaml).
- **Scan** : activez un scanner (YARA/AV) si vous stockez des fichiers (`scanner`/`scan_command`).
- Ignorez/retirez du VCS les artefacts de scrape (docs/, data/cache*, logs/, reports/).

## IA et données
- Désactivez le rapport IA si non nécessaire (`--no-ai-report`). Ne transmettez pas de données sensibles aux modèles.
- Le scoring IA ne doit pas servir à inventer ni à hiérarchiser des cibles non consenties.

## Headless / JS
- N’activez `headless` que pour des pages autorisées. La stratégie est extensible (Playwright/Selenium) mais reste soumise à l’allowlist et aux garde-fous.

## Monitoring et traçabilité
- Surveillez `logs/` et `data/health.json` (fetch total/succès/échecs/durée). Utilisez `scripts/health_summary.py` (option `--prometheus`) pour superviser.
- Ajoutez des alertes si des domaines hors allowlist apparaissent ou si le taux d’échec augmente.

## Ce qu’il ne faut pas faire
- Pas d’accès à des réseaux privés ou internes sans consentement explicite.
- Pas de scraping de données protégées/sensibles ou nécessitant authentification sans autorisation formelle.
- Ne désactivez pas les garde-fous (allowlist, block_private, robots, limites) pour “tout aspirer”.
- **Exemples à ne pas faire** :
  - Mettre `allow_domains: ["*"]` ou vider l’allowlist.
  - Définir `block_private: false` puis cibler des IP privées (10.x, 192.168.x, 172.16/12).
  - Passer `respect_robots: false` et `max_depth`/`max_pages` à des valeurs énormes pour tout aspirer.
  - Activer `headless` sur des sites non autorisés ou nécessitant authentification.
  - Commiter des tokens/API keys dans `config/auth.yaml` ou des proxies non maîtrisés.
  - Bypasser la sandbox (`sandbox_dir`) ou supprimer les scans/limites de taille pour ingérer tout type de fichier.

En résumé : allowlist stricte, HTTPS + blocage privé, sandbox + limites (depth/pages/bytes/délai), secrets protégés, headless seulement si besoin, monitoring des logs/métriques. Toute levée de garde-fous doit être explicitement autorisée.***
