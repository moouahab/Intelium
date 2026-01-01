# DevSecOps Guide - Analyse des metriques

Ce guide explique comment lire et exploiter les metriques du scraper pour l'exploitation, la securite et la qualite.

## Flux des metriques
1) Le scraper ecrit ses stats dans `data/health.json`.
2) `scripts/metrics_server.py` expose deux endpoints:
   - `/metrics` (Prometheus)
   - `/health` (JSON)
3) Prometheus scrappe `/metrics`.
4) Grafana affiche les panels.
5) Alertmanager declenche les alertes (regles dans `srcs/prometheus_rules.yml`).

## Metriques disponibles (Prometheus)
- `cti_fetch_total`: nombre total de fetch.
- `cti_fetch_success`: nombre de fetch reussis.
- `cti_fetch_failure`: nombre de fetch en erreur.
- `cti_fetch_avg_duration_seconds`: duree moyenne d'un fetch.
- `cti_fetch_bytes_total`: volume total telecharge.
- `cti_runs_total`: nombre total de runs.
- `cti_runs_success`: runs reussis.
- `cti_runs_failure`: runs en echec.
- `cti_fetch_reason_total{reason="..."}`: compteur par raison (error, blocked-robots, offline, etc.).
- `cti_fetch_status_total{status="..."}`: compteur par statut (downloaded, skipped-cache, offline, skipped-quota, etc.).

## Reponses rapides (ce que signifie la metrique)
- **`cti_fetch_failure` monte vite**: erreurs reseau, robots, MIME, quota, ou allowlist.
- **`cti_fetch_avg_duration_seconds` augmente**: sources lentes, timeouts trop longs, blocage reseau.
- **`cti_fetch_status_total{status="skipped-quota"}` augmente**: quota global atteint.
- **`cti_fetch_status_total{status="offline"}` augmente**: mode offline active sans cache.
- **`cti_fetch_status_total{status="skipped-cache"}` augmente**: run majoritairement seed/cache.

## PromQL utiles (a coller dans Prometheus/Grafana)
- Taux d'echec fetch (10 min):
  - `increase(cti_fetch_failure[10m]) / increase(cti_fetch_total[10m])`
- Taux de succes fetch (10 min):
  - `increase(cti_fetch_success[10m]) / increase(cti_fetch_total[10m])`
- Repartition des statuts:
  - `sum by (status) (cti_fetch_status_total)`
- Top erreurs par raison:
  - `sum by (reason) (cti_fetch_reason_total)`
- Quota atteint (30 min):
  - `increase(cti_fetch_status_total{status="skipped-quota"}[30m])`
- Offline/cache-only (30 min):
  - `increase(cti_fetch_status_total{status="offline"}[30m])`
  - `increase(cti_fetch_status_total{status="skipped-cache"}[30m])`

## Alertes par defaut
Regles dans `srcs/prometheus_rules.yml`:
- **CTIHighFetchFailureRate**: > 40% de fetch en echec (10 min).
- **CTIHighRunFailureRate**: > 20% de runs en echec (1h).
- **CTIMetricsMissing**: endpoint metrics down.
- **CTIQuotaTriggered**: quota global atteint.

## Lecture securite (DevSecOps)
- **Blocage robots/allowlist**: peut signaler un changement de politique ou un domaine non autorise.
- **Erreur TLS/SSL**: peut signaler interception, certificat invalide, ou mauvaise config CA.
- **Offline/seed**: utile en mode incident (pas de reseau), mais doit etre explicite dans le rapport.

## SLO simples (exemple)
- Fetch success rate > 90% sur 1h.
- Run failure rate < 10% sur 1h.
- `cti_fetch_avg_duration_seconds` stable (pas de derive brutale).

## Interpretation par symptome
| Symptom | Cause probable | Action |
| --- | --- | --- |
| Echecs fetch eleves | Robots, allowlist, timeouts, MIME | Verifier `network.yaml`, `crawler.yaml`, sources |
| Quota atteint | `global_max_pages`/`global_max_bytes` trop bas | Ajuster quotas ou filtrer les sources |
| Offline dominant | Mode offline actif sans cache | Desactiver offline ou remplir le cache Mongo |
| Metrics down | `cti-metrics` stoppe | Verifier le service metrics et la config Prometheus |

## Ou regarder dans Grafana
- Dashboard `CTI - Overview`
- Panels recommandés:
  - Fetch success/failure
  - Status distribution
  - Top error reasons
  - Run success/failure
