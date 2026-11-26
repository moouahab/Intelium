# Analyse Intelium et audit de sécurité

Audit du 25 novembre 2026 sur l’arbre de travail associé au commit `b0d797d1ad30ca9e5918542f87ea89b6c0f664f2`, modifications locales comprises. Intelium est un agent CTI de collecte et de production de rapports. La configuration livrée nécessite un durcissement avant une exposition en production, particulièrement pour MongoDB et la confiance accordée au cache.

Cette documentation constitue la mémoire persistante de cette analyse. Elle ne garantit pas une mémorisation automatique dans une autre conversation. [L’inventaire](FUNCTIONS.md) et [les données détaillées](functions.json) permettent de retrouver les fonctions, signatures, opérations et usages candidats. L’inventaire couvre toutes les définitions Python détectées, pas une validation manuelle exhaustive de chaque fonction. Les appels dynamiques, alias et constructeurs ne sont pas résolus par l’outil ; un nom commun peut produire plusieurs faux candidats.

## À quoi sert le projet

Intelium collecte des pages HTML, flux XML/RSS, API JSON, CSV, textes, PDF et images. Il extrait du texte, des mots-clés et des indicateurs cyber, calcule des scores, conserve un cache et produit des rapports Markdown/JSON/PDF. Une synthèse IA et un envoi email sont configurables. L’orchestrateur planifie les exécutions ; des métriques alimentent Prometheus, Grafana et Alertmanager. MongoDB stocke cache et résultats ; Vault fournit une intégration de secrets.

Le projet aide à la veille et à la priorisation. Il ne prouve ni l’exploitation d’une CVE, ni la pertinence d’un IOC pour le système d’information de l’utilisateur. La présence d’un marqueur de fin et de titres dans une réponse IA ne valide pas ses affirmations.

## Chemin principal et responsabilités

| Étape | Fonctions et composants | Utilisation |
| --- | --- | --- |
| Entrée | `main.py`, `runner.run` | Arguments CLI, lecture de configuration, contrôles d’environnement et d’allowlist |
| Configuration | `ConfigModel`, `load_yaml_config`, `_deep_merge` | Fusion des YAML, construction des sources et politiques |
| Pipeline | `run_pipeline`, `build_cache_manager`, `run_fetch` | Création du run_id, choix du cache, lancement du scraper |
| Exploration | `Scraper.run`, `_process_single`, `_worker_loop`, `_process_source`, `CrawlerState` | File de crawl, profondeur, quotas, parallélisme, cache |
| Acquisition | `_fetch_and_parse`, `HttpClient.fetch`, `build_request_context`, `get_response` | Authentification, robots, délais, validation réseau et redirections |
| Persistance des téléchargements | `download_with_context`, `_persist_content`, `run_scan` | Taille, confinement des écritures, scan avant publication atomique |
| Extraction | `Extractor.extract`, `parse_content`, registre des parseurs | Routage HTML/JSON/XML/CSV/TXT/PDF/OCR, IOC, mots-clés |
| Enregistrement | `ResultRecorder`, caches fichier/Mongo, `result_store` | Statuts, extraits, hash, chemin, métadonnées du run |
| Préparation | `enrich_results`, `prepare_results`, `score_results_payload` | Complément depuis fichiers, normalisation et scoring |
| Rapport technique | `run_report`, `write_report`, `ReportWriter.write` | Markdown, JSON, détails par source, vues supplémentaires |
| Synthèse | `generate_ai_report`, `DefaultAIProvider.generate`, `PromptConfig.build_prompt`, `run_cli_llm` | Compactage, prompt, commande IA, retries/fallback, contrôle de forme |
| Distribution | `send_report_email`, `_ensure_pdf` | Rendu PDF et SMTP après génération |
| Exploitation | `cti_core/orchestrator.py`, `tools/scheduling.py`, `scripts/metrics_server.py` | Planification, santé, exposition des métriques |

Les interfaces de `tools/interfaces.py` permettent d’injecter cache, fetcher, parser et fournisseur IA. Les tests exploitent ces points d’injection. Le JSON d’inventaire donne les sites d’appels candidats pour chaque fonction ; les liens du Markdown conduisent à son implémentation.

## Périmètre et preuves

Revue du code, des configurations et de l’assemblage Docker ; exécution de tests locaux et de reproductions avec mocks et fichiers factices. Aucun service n’a été démarré pour cet audit, aucun email envoyé, aucun appel IA effectué. L’accessibilité réseau réelle dépend du déploiement et du pare-feu et n’a pas été mesurée. Aucun inventaire CVE des dépendances ou images n’a été exécuté : ne pas interpréter ce rapport comme une attestation d’absence de CVE. Les fichiers de secrets et les bases réelles n’ont pas été inspectés.

Les modifications préexistantes ont été conservées. Les protections déjà présentes dans cet arbre incluent la validation des redirections, le retrait des headers applicatifs lors d’un changement d’origine, le refus DNS en cas d’échec de résolution, le blocage du headless avec politique restrictive et le rejet YARA avant publication. Ces points ne doivent pas être signalés comme absents sur la base d’un ancien état du code.

## Constats prioritaires

### A01 MongoDB sans authentification configurée et publié sur l’hôte

**Priorité P1, gravité élevée, configuration confirmée.** `srcs/docker-compose.yml:47` publie `27017:27017`, sans configuration d’authentification dans le service. Si ce port est accessible et que le service utilise cette configuration, un tiers peut lire ou modifier les données, notamment le cache. Une configuration externe peut changer ce constat au runtime.

Reproduction statique : examiner le bloc `mongo` du Compose. Correction : retirer la publication si inutile, sinon limiter l’écoute à une interface de confiance ; activer l’authentification et créer un utilisateur applicatif limité. Validation attendue sur une instance de test : une lecture sans identifiants doit être refusée et le port ne doit pas être accessible depuis un réseau non autorisé.

### A02 Le cache peut déclencher une lecture de fichier hors sandbox

**Priorité P1, gravité élevée, reproduction locale confirmée.** `cti_core/scraper.py:83` accepte `saved_path`, appelle `read_bytes()` puis transmet le contenu au parseur sans confinement, plafond de taille ni vérification de hash. `cti_core/pipeline_steps.py:enrich_results` présente un chemin similaire. Condition : possibilité de modifier le cache ou les résultats fournis au pipeline. A01 peut fournir cette possibilité. Les extraits falsifiés du cache sont également acceptés directement.

Impact : lecture d’un fichier accessible au processus et contamination des rapports. Une transmission vers le fournisseur IA ou par email est possible selon les étapes activées, mais cette chaîne n’a pas été exécutée. `python3 docs/audit/reproduce.py` démontre uniquement la lecture d’un fichier factice hors sandbox. Correction : traiter le cache comme non fiable, confiner les chemins canoniques, contrôler taille et intégrité, associer les artefacts à un run et protéger les écritures dans le cache. Tester aussi les liens symboliques et les entrées contenant directement des extraits falsifiés.

### A03 Validation DNS séparée de la connexion

**Priorité P1, gravité élevée conditionnelle.** `tools/providers/http/network.py:53` valide les IP résolues, puis `:86` transmet le nom d’hôte à `requests.get`. La connexion n’est pas liée à l’IP validée. Une résolution différente ou celle d’un proxy peut contourner la vérification si l’attaquant contrôle un domaine autorisé ou si l’allowlist est élargie. HTTPS avec certificat valide et allowlist stricte réduisent les possibilités ; aucun SSRF réel n’a été démontré.

La reproduction mockée vérifie le passage du hostname au transport, pas une connexion privée. Correction : imposer un contrôle de destination au niveau du transport ou d’un proxy de sortie, avec vérification TLS/SNI conservée et blocage réseau des destinations internes. Le risque de séparation entre validation et usage est documenté par [OWASP SSRF](https://top10.owasp.org/2021/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/).

### A04 Grafana par défaut et interfaces de supervision exposées

**Priorité P1, gravité élevée pour Grafana si valeurs par défaut effectives.** `srcs/docker-compose.yml:104` et `:105` utilisent `admin/admin` en l’absence de variables. Les ports 3000, 9000, 9090 et 9093 sont publiés sans restriction d’interface dans Compose. Les contrôles d’accès d’un éventuel proxy externe n’ont pas été évalués.

Correction : secret obligatoire sans valeur de secours, interfaces de gestion sur réseau privé et accès authentifié. Reproduction : inspecter les valeurs de secours et les mappings du Compose sans afficher l’environnement réel. Validation : le déploiement doit refuser un secret absent ; les interfaces doivent être inaccessibles depuis un réseau non autorisé.

### A05 Isolation insuffisante des contenus externes

**Priorité P2, gravité moyenne à élevée selon les entrées.** Le Dockerfile ne définit pas de `USER`, le Compose monte `/app` en écriture et transmet tout `.env` à plusieurs services. `ocr_parser.py:50` appelle Tesseract sans timeout ; `pdf_parser.py:85` extrait le texte avant de le tronquer. Les limites de caractères ne sont pas des limites CPU/mémoire. `sandbox_dir` confine des écritures, ce n’est pas une isolation du processus.

Reproduction statique : lire ces appels et les paramètres Docker. Aucun document visant à épuiser les ressources n’a été exécuté. Correction : utilisateur non privilégié, montage du code en lecture seule, secrets minimaux par service, limites CPU/mémoire/PID et traitement PDF/OCR dans un processus à durée limitée. Tester les dépassements de durée avec des mocks lents contrôlés.

### A06 Secrets potentiels dans les logs de débogage

**Priorité P2, gravité moyenne, omission Cookie confirmée.** `mask_sensitive_headers` ne masque pas `Cookie`. `HttpClient.fetch` journalise aussi l’URL et le proxy brut ; des credentials de proxy ou tokens dans la query peuvent apparaître. `runner.run` journalise la configuration complète en DEBUG ; le risque dépend des valeurs présentes dans celle-ci.

Reproduction : le script local confirme qu’un Cookie factice reste visible. Correction : liste blanche de champs de log, suppression des identifiants URL/proxy, masquage Cookie et des champs secrets récursifs. Validation avec sentinelles factices dans chaque champ ; aucune sentinelle ne doit apparaître dans les logs.

### A07 Données externes dans le prompt et transfert vers Mistral

**Priorité P2, risque d’intégrité et de confidentialité conditionnel.** `PromptConfig.build_prompt` insère les extraits dans le prompt ; `scripts/mistral_llm.py` les transmet à `https://api.mistral.ai/v1/chat/completions`. Le commentaire « pas d’accès réseau » dans `ai_report.py` décrit mal la commande configurée. Le contenu d’une source peut comporter des instructions malveillantes. Aucune exécution de commandes par le modèle ni extraction effective de secrets n’est démontrée.

Correction : distinguer clairement instructions et données, retirer les informations sensibles, imposer des références aux sources et une validation humaine avant usage opérationnel. Documenter le fournisseur externe. Tester des sources synthétiques contenant des instructions contradictoires avec un fournisseur factice ; ne pas attribuer à `is_complete` une garantie factuelle.

### A08 Initialisation Vault défectueuse et divulgation prévue des clés

**Priorité P2, fiabilité et gestion des secrets.** `init_vault.sh:57` affecte `INIT_OUT` sans export, alors que les sous-processus Python la lisent via `os.environ` aux lignes 61 et 68. Sauf export hérité, cela échoue après l’initialisation. La branche existante combine un pipe et `python -` avec heredoc : stdin sert au script, pas au JSON attendu. Le script prévoit aussi d’afficher le token root et la clé d’unseal.

Reproduction statique uniquement, sans initialiser Vault. Correction : transmission JSON explicite et sûre, traitement idempotent de l’état, conservation sécurisée des clés et token applicatif à droits limités. Tester le script avec un faux binaire Docker renvoyant des états initialized/sealed, jamais avec une instance réelle pour reproduire ces erreurs.

### A09 Contrôles de chaîne de construction incomplets

**Priorité P2.** La CI vérifie que le fichier racine `.env` n’est pas suivi ; ce n’est pas un détecteur de secrets dans les autres fichiers ou l’historique. Le Dockerfile fait `COPY . .` sans `.dockerignore` trouvé dans le contexte. Les images `latest` et tags sans digest ne garantissent pas une reconstruction identique.

Correction : exclusions explicites du contexte Docker, scan de secrets, audit des dépendances/images, SBOM et digests des images. Ne pas déclarer de CVE particulière sans résultat de scan correspondant à la version construite.

## Reproductibilité des rapports CTI

La reproductibilité exacte n’est pas assurée aujourd’hui. Les sources changent, le cache téléchargé est réutilisé sans expiration dans `_process_source`, les fichiers téléchargés vont par défaut dans un répertoire temporaire et les sorties utilisent des chemins fixes. Un cache hit retourne avant l’exploration des liens : un second crawl n’est donc pas nécessairement équivalent au premier. Le parallélisme peut modifier l’ordre des résultats. Le modèle par défaut `mistral-large-latest` est un alias et la température vaut 0,2.

`config/output.yaml` utilise le même chemin pour le rapport technique et IA, accepte des réponses incomplètes et désactive la restauration du rapport technique. Le JSON technique demeure une sortie distincte, mais le Markdown principal peut perdre son contenu initial. Un rapport formellement complété par des titres ajoutés ne constitue pas une analyse complète.

Pour obtenir un rapport vérifiable, créer un dossier immuable par run contenant :

1. Commit, empreintes des modifications locales, versions Python/dépendances et digests d’images.
2. Configuration effective expurgée, règles YARA, mots-clés, versions des parseurs et du scoring.
3. Artefacts sources avec SHA-256, URL finale, horodatage UTC, état HTTP et métadonnées de collecte utiles, sans credentials.
4. État du cache et liste des sources manquantes ou échouées ; politique de fraîcheur explicite.
5. Résultats normalisés triés avec règle stable, puis rapport technique séparé du rapport IA.
6. Prompt exact protégé, fournisseur, version précise du modèle, paramètres, réponse brute et usage du fallback. Une température nulle seule ne garantit pas l’identité d’une réponse distante.
7. Empreintes des sorties JSON/Markdown/PDF, statut complet/incomplet et provenance de chaque conclusion importante.

Rejouer d’abord le rendu technique à partir des résultats JSON figés, sans fetch, IA ni email. Comparer les empreintes après avoir fixé les champs temporels et l’ordre. Rejouer ensuite l’extraction sur les artefacts figés pour tester les parseurs. Pour reproduire exactement la synthèse, réutiliser la réponse IA archivée ; un nouvel appel mesure une nouvelle génération. Ne pas utiliser `--no-ai-report` comme garantie de fonctionnement hors ligne : ce drapeau ne désactive ni la collecte ni l’email.

## Tests et reproduction de cet audit

Commandes exécutées depuis `srcs/requirements/app` avec Python 3.14 :

```sh
python3 -m pytest -q
# Arrêt de collecte : mongomock absent.
python3 -m pytest -q --ignore=tests/test_storage_mongo_mock.py
# 172 passed, 2 failed.
```

Échecs : `test_send_report_email_attaches_pdf` et `test_parse_image_uses_languages_and_limits`. `pytesseract` est absent dans cet environnement ; le test force le drapeau OCR sans restaurer toutes les dépendances initialisées lors de l’import. L’échec PDF nécessite une vérification dans l’environnement verrouillé avant d’être classé comme régression applicative. Aucune réussite complète de CI n’est revendiquée.

Depuis la racine du dépôt :

```sh
python3 docs/audit/inventory.py
python3 docs/audit/reproduce.py
git diff --check
```

Résultats des reproductions : lecture factice hors sandbox confirmée ; Cookie factice non masqué confirmé ; hostname conservé jusqu’au transport confirmé. Le script ne fait aucune requête réseau. `functions.json` contient le commit et les SHA-256 des modules analysés pour détecter une dérive. Les fichiers hors Python sont identifiés dans `snapshot.json` par leurs empreintes. Aucun secret réel n’est copié dans ces artefacts.

## Ordre de traitement

1. **Avant exposition** : A01, A02 et A04 ; fermer les interfaces inutiles et protéger le cache.
2. **Avant collecte non maîtrisée** : A03, A05 et A06 ; contrôler les sorties réseau, isoler les parseurs, expurger les logs.
3. **Avant diffusion opérationnelle** : A07 et reproductibilité ; préserver le rapport technique et afficher les limites de collecte/synthèse.
4. **Avant déploiement durable** : A08, A09, environnement de test complet, sauvegarde/restauration et rétention documentées.

Les corrections applicatives ne sont pas incluses dans cette livraison d’audit. Les seuls ajouts sont les documents et les scripts d’inventaire/reproduction sous `docs/audit`.
