# Audit Final - Go/No-Go (Niveau Entreprise)

Ce fichier sert de checklist finale avant passage en production.

## Securite & conformite
- [ ] Allowlist non vide (`ops.require_allowlist: true`) + cohérente avec `sources`.
- [ ] `block_private: true` et `enforce_https: true` actifs.
- [ ] Secrets uniquement via `.env`/Vault, aucun secret en dur dans les YAML.
- [ ] `sandbox_dir` configure, `scan_command` valide (ou scan desactive explicitement).
- [ ] Robots/delais respectes, overrides justifies.
- [ ] `.env` non commit + headers sensibles masques dans les logs.

## Fiabilite d'execution
- [ ] Run complet OK (reseau + IA).
- [ ] Mode offline/seed OK et signale dans le rapport.
- [ ] Rapport complet (sections requises + FIN DU RAPPORT).
- [ ] Alertmanager OK (pas de reboot loop).
- [ ] Trace run_id/run_started_at presente en Mongo.

## Qualite donnees
- [ ] PDF/OCR stables (limites, langues, min_chars).
- [ ] Dedup/normalisation actives.
- [ ] Extraction CVE/IOC coherente et sourcée.
- [ ] Fallback IA si rapport incomplet.

## Observabilite
- [ ] `/metrics` et `/health` OK.
- [ ] Prometheus target UP.
- [ ] Dashboard Grafana OK (success/failure, statuts, dernier run).
- [ ] Alertes actives (quota, metrics down, dernier run KO).
- [ ] Test notification email/Slack OK.

## Stockage & reprise
- [ ] Mongo contient `cache` + `results`.
- [ ] Cache reutilise (statut `skipped-cache` coherents).
- [ ] Strategie retention/backup definie si volume important.

## CI & tests
- [ ] CI passe sur PR.
- [ ] Tests Mongo mockes OK.
- [ ] Check anti-secret en CI OK.
