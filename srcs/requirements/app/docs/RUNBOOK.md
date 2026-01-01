# Runbook – Vérifier les services

Ce guide décrit quoi vérifier après un redémarrage et comment tester chaque service sans casser le run.

## Après redémarrage (checklist rapide)
1) **Scraper** : le run démarre, aucun message “variables d’environnement manquantes”, et `reports/rapport.md` est mis à jour.
2) **Metrics** : la page `http://localhost:9000/health` répond (statut OK) et `http://localhost:9000/metrics` expose des compteurs.
3) **Prometheus** : `http://localhost:9090/targets` montre `cti-metrics:9000` en **UP**.
4) **Alertmanager** : `http://localhost:9093` s’ouvre et la configuration est chargée (pas d’erreur “unsupported scheme”).
5) **Grafana** : `http://localhost:3000` (login par défaut `admin/admin` si pas changé) et le dashboard “CTI - Overview” s’affiche.
6) **Mongo** : la base contient des documents après un run (collections `cache` et `results`).
7) **Vault (si utilisé)** : l’état indique `sealed: false` et la clé `VAULT_SECRET_PATH` est accessible.

## Tests par service

### Scraper (cti-scraper)
- **Attendu** : un rapport principal (`reports/rapport.md`) + détails (`reports/sources_user/`) + fichiers scrappés (`docs/`).
- **À surveiller dans le rapport** :
  - La section “Résumé du run” contient un statut cohérent.
  - Si aucune source n’a été téléchargée, un avertissement “100% cache/seed” est présent.

### Metrics (cti-metrics)
- **URL** : `http://localhost:9000/metrics`
- **Attendu** : métriques Prometheus lisibles (compteurs de runs, statuts, erreurs).

### Prometheus
- **URL** : `http://localhost:9090/targets`
- **Attendu** : target `cti-metrics` en **UP**.

### Grafana
- **URL** : `http://localhost:3000`
- **Attendu** : datasource Prometheus active + dashboard “CTI - Overview”.

### Alertmanager
- **URL** : `http://localhost:9093`
- **Attendu** : page de statut accessible, config chargée.
- **Note** : si les variables d’alerting sont vides, Alertmanager démarre quand même, mais les notifications ne partent pas. Renseigner les vraies valeurs dans `.env`.

### MongoDB
- **Attendu** : après un run, la base `cti` contient des données (`cache` et `results`).
- **Astuce** : si le rapport indique beaucoup de `skipped-cache`, c’est que le cache Mongo est bien utilisé.

### Vault (si utilisé)
- **Attendu** : `sealed=false` et accès au chemin `VAULT_SECRET_PATH`.
- **Note** : en environnement dev, l’init/unseal est nécessaire avant usage.

## Problèmes fréquents
## Symptômes → Causes → Actions

| Symptôme | Cause probable | Action |
| --- | --- | --- |
| Alertmanager redémarre en boucle | Variables d’alerting vides/invalides | Renseigner `SLACK_WEBHOOK_URL`, `ALERT_EMAIL_*`, `SMTP_*` dans `.env` |
| Port 9093 fermé | Alertmanager n’a pas chargé sa config | Vérifier le log du conteneur et corriger les variables d’alerting |
| Scraper s’arrête immédiatement | Pré‑check strict et env manquantes | Ajouter les variables exigées ou désactiver `ops.strict_env` |
| Rapport “vide” | Sources bloquées (robots/cache) ou offline sans cache | Vérifier le statut “skipped-cache/offline”, relancer avec accès réseau |
| Rapport “100% cache/seed” | Aucun download réseau | Vérifier allowlist/robots/proxy et la connectivité |
| Métriques non visibles | Service metrics KO ou port non exposé | Vérifier `cti-metrics`, port `9000`, et que Prometheus pointe dessus |
| Prometheus cible DOWN | Metrics pas joignable | Vérifier `cti-metrics`, réseau Docker, port `9000` |
| Grafana sans données | Datasource Prometheus non OK | Vérifier datasource et URL `http://prometheus:9090` |
| Mongo vide | `MONGO_URI` absent ou mauvais | Vérifier `.env` et connectivité Mongo |
| Vault sealed | Vault non initialisé/unseal | Lancer init/unseal et renseigner `VAULT_TOKEN` |

## Problèmes fréquents
- **Alertmanager qui redémarre en boucle** : variables d’alerting vides ou invalides.
- **Scraper qui s’arrête immédiatement** : pré-check strict (`ops.strict_env: true`) et variables manquantes.
- **Rapport “vide”** : sources bloquées (robots, cache) ou mode offline sans cache.
