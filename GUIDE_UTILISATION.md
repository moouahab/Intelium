# Guide d’utilisation Intelium

Intelium collecte des renseignements cyber publics, classe les contenus et produit un rapport avec des preuves. Ollama aide à sélectionner les éléments à examiner ; le programme rédige le rapport en français à partir des données sources. Intelium ne détecte pas directement les attaques sur ton réseau et ne modifie pas tes équipements.

## 1. Préparer le poste

Ouvre un terminal à la racine du dépôt. Il faut Docker démarré, Docker Compose, `make`, une connexion Internet et plusieurs Go d’espace pour les images et le modèle.

```sh
docker --version
docker compose version
make help
```

Le modèle par défaut est `qwen2.5:1.5b`. La génération de vérification a été testée sur une machine disposant de 4 Go de RAM ; prévoir une à plusieurs minutes selon le matériel. Le premier démarrage est plus long à cause des téléchargements.

Sous Linux, si ton utilisateur n’a pas les identifiants 1000/1000, définis-les avant de lancer le conteneur de vérification :

```sh
export LOCAL_UID="$(id -u)"
export LOCAL_GID="$(id -g)"
```

## 2. Produire ton premier rapport

```sh
make verify-report
```

Cette commande construit l’application, démarre Ollama, attend le téléchargement du modèle, collecte les trois jeux structurés et génère le rapport. Elle utilise les contrôles réseau et YARA du projet. Elle ne demande aucune clé API et n’envoie aucun email.

Les trois jeux sont :

| Source | Ce qu’elle apporte |
| --- | --- |
| CISA KEV en CSV | Vulnérabilités exploitées, produits concernés, dates et actions publiées |
| Feodo en CSV | Indicateurs de serveurs de commande et contrôle, familles de malware et dates d’observation |
| MITRE ATT&CK en STIX JSON | Techniques, tactiques et plateformes de référence |

Le résultat apparaît dans :

```text
srcs/requirements/app/reports/verification/rapport_ia.md
```

Ouvre ce fichier dans ton éditeur ou ton lecteur Markdown. La dernière ligne affichée dans le terminal indique notamment `validation`, `sources_with_data` et `sources_expected`. Une vérification réussie indique `passed` et trois sources avec des données ; sinon, la commande retourne un code d’erreur et conserve les résultats pour le diagnostic.

## 3. Lire et exploiter les résultats

Commence par les priorités et les actions proposées, puis consulte leurs citations et les champs complets des sources. Pour une CVE, vérifie le produit et la version sur tes propres machines avant de décider d’un correctif.

| Fichier dans `reports/verification/` | Utilité |
| --- | --- |
| `rapport_ia.md` | Rapport français avec sélection assistée par Ollama |
| `rapport_ia.quality.json` | Statut des contrôles, erreurs, paramètres et empreintes |
| `technical.md` et `technical.json` | Résultats techniques de la collecte |
| `results.json` | Données d’entrée conservées pour rejouer la génération |
| `summary.md` | Résumé technique des priorités calculées |
| `iocs.csv` et `iocs.json` | Export des indicateurs extraits ; leur présence ne prouve pas qu’ils sont malveillants |
| `raw/` | Contenus sources décodés et scannés |
| `runs/<run_id>/attack_types.csv` | Types d’attaque, références, dates et actions, avec identifiants de preuve |
| `runs/<run_id>/evidence.json` | Ensemble des preuves retenues par le traitement |
| `runs/<run_id>/request.json` et `response.json` | Requête et réponse Ollama ; réponse absente si l’appel échoue |

Le rapport contient des liens vers ses exports et son contrôle qualité. Le CSV s’ouvre dans un tableur ; filtre par source, type d’attaque ou identifiant pour examiner les résultats.

Trois distinctions sont essentielles :

- `passed` signifie que les contrôles automatisés réussissent, pas que l’organisation est certifiée ou que chaque source dit vrai.
- Une technique MITRE est une référence, pas une attaque détectée chez toi.
- Une entrée Feodo marquée `historical_activity` concerne une observation ancienne : ne bloque pas automatiquement l’adresse sur cette seule base.

Les catégories d’attaque reposent sur des mentions dans les textes. Leurs comptages ne représentent pas le nombre d’incidents. Ollama examine un échantillon borné de preuves ; les autres éléments restent disponibles dans les exports.

## 4. Relancer ou rejouer

Pour collecter à nouveau les trois sources et produire un nouveau rapport :

```sh
make verify-report
```

Le rapport courant est actualisé. Chaque génération dispose aussi de son dossier `runs/<run_id>/` pour conserver les résultats précédents.

Pour refaire uniquement la génération IA sur les données déjà collectées, sans nouvelle collecte :

```sh
make ollama-start
make ollama-status
# Attendre que qwen2.5:1.5b soit disponible.
docker compose -f srcs/docker-compose.yml run --rm --no-deps cti-verify \
  python scripts/verify_cti_report.py \
  --results reports/verification/results.json \
  --output-dir reports/verification/replay
```

Un rejeu appelle à nouveau le modèle et peut produire une sélection différente. Pour retrouver exactement un ancien résultat, ouvre son rapport archivé et sa réponse Ollama.

## 5. Régler Ollama

Pour connaître les modèles disponibles :

```sh
make ollama-status
```

Pour changer de modèle, définis `OLLAMA_MODEL` avant le démarrage et la vérification :

```sh
export OLLAMA_MODEL=qwen2.5:1.5b
make ollama-start
make verify-report
```

Remplace la valeur par le modèle voulu, en tenant compte de ta mémoire disponible. Pour augmenter le délai d’attente :

```sh
export OLLAMA_TIMEOUT=300
make verify-report
```

Le service de vérification utilise le serveur Docker interne, un contexte de 4096 et un budget de sortie de 1024. Pour ses autres réglages, modifie son bloc `environment` dans `srcs/docker-compose.yml`. Les réglages et limites du fournisseur sont décrits dans [le guide Ollama CTI](srcs/requirements/app/docs/OLLAMA_CTI.md).

## 6. Ajouter une source CSV

Dans `srcs/requirements/app/config/sources.yaml`, ajoute une entrée en remplaçant l’URL d’exemple :

```yaml
  - name: MA-SOURCE-CSV
    url: https://flux.example.org/menaces.csv
    type: csv
```

Ajoute `flux.example.org` à `network.allow_domains` dans `network.yaml`. Dans `scraping.yaml`, ajoute les paramètres sous `data_scraper.per_source` :

```yaml
    MA-SOURCE-CSV:
      csv:
        record_format: json
        select_columns: [identifier, description, date, action]
        sort_by: date
        descending: true
        max_rows: 100
```

Les noms de colonnes doivent correspondre au fichier réel. Le tri des dates suppose un format lexical compatible, par exemple ISO 8601. L’ajout d’un CSV ne suffit pas à interpréter automatiquement toutes ses colonnes : les règles CTI peuvent nécessiter une adaptation.

`make verify-report` reste volontairement limité aux trois jeux de vérification. Une nouvelle source est utilisée par le pipeline général, présenté ci-dessous.

## 7. Utiliser la collecte générale et la planification

Cette étape démarre aussi les services de stockage et de supervision. Pour un premier essai, le mode de vérification précédent suffit.

Si `.env` n’existe pas encore :

```sh
cp .env.example .env
```

Renseigne les valeurs nécessaires au mode choisi, notamment `MONGO_URI` et `OTX_API_KEY` si la source OTX reste activée. Les valeurs `changeme` sont des exemples, pas des identifiants utilisables. Ne publie pas `.env`.

Avant d’activer la stack, vérifie :

- `config/output.yaml` : l’envoi email y est activé par défaut ; mets `email_report.enabled: false` si tu ne souhaites pas d’envoi.
- `config/scheduling.yaml` : intervalle, heure, fuseau et destinataires ; adapte les valeurs à ton usage.
- [L’audit de sécurité](docs/audit/README.md) : les services MongoDB et de supervision nécessitent un durcissement avant exposition à un réseau non maîtrisé.

Depuis la racine :

```sh
make run
make logs
```

Pour une exécution immédiate du pipeline général, indépendamment de l’horaire planifié :

```sh
docker compose --env-file .env -f srcs/docker-compose.yml run --rm --no-deps \
  cti-scraper python main.py --config config/conf.yaml
```

Cette exécution utilise la configuration générale, y compris l’email si tu le laisses activé. `--no-ai-report` désactive seulement l’IA : il ne désactive ni la collecte ni l’email.

Les rapports généraux se trouvent dans `srcs/requirements/app/reports/rapport.md`, `rapport.json` et `rapport_ia.md`. Le cache général est rafraîchi après 900 secondes par défaut ; le mode de vérification récupère directement les flux.

## 8. Dépanner et arrêter

| Symptôme | Vérification à effectuer |
| --- | --- |
| Le modèle manque | `make ollama-status`, puis `docker compose -f srcs/docker-compose.yml logs --tail 30 ollama-init` |
| Le rapport indique `failed` | Lire `rapport_ia.quality.json`, puis les statuts de collecte dans `results.json` |
| `ReadTimeout` | Vérifier RAM/CPU, fermer les tâches lourdes ou augmenter `OLLAMA_TIMEOUT` |
| Source bloquée ou vide | Examiner l’erreur HTTP/robots/YARA, l’allowlist et les limites ; ne pas désactiver les contrôles pour masquer l’erreur |
| Permission refusée dans les rapports | Vérifier `LOCAL_UID`, `LOCAL_GID` et le propriétaire du dossier de sortie |
| Le pipeline général s’arrête avant collecte | Vérifier les variables requises et la cohérence des sources avec l’allowlist |

Pour arrêter uniquement Ollama en conservant le modèle téléchargé :

```sh
docker compose -f srcs/docker-compose.yml stop ollama ollama-init
```

Pour arrêter la stack et conserver ses volumes :

```sh
docker compose -f srcs/docker-compose.yml down
```

N’utilise pas `make fclean` pour un simple arrêt : cette cible supprime des rapports, caches et volumes. Les rapports et archives sont ignorés par Git ; sauvegarde ceux que tu souhaites conserver.

## Pour aller plus loin

- [Fonctionnement détaillé d’Ollama et des preuves](srcs/requirements/app/docs/OLLAMA_CTI.md)
- [Cartographie des fonctions](docs/audit/FUNCTIONS.md)
- [Audit et reproductibilité](docs/audit/README.md)
