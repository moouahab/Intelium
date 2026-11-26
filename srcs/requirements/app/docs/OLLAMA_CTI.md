# Rapports Ollama et sources structurées

Le fournisseur IA par défaut utilise l’API locale Ollama pour sélectionner et ordonner les preuves à examiner, avec des codes d’action bornés par un catalogue. Le programme rédige ensuite le rapport en français depuis les champs sources ; il ne publie pas de prose libre du petit modèle. Le rapport technique reste dans `reports/rapport.md` et la synthèse sourcée dans `reports/rapport_ia.md`. Les erreurs Ollama ne suppriment pas les preuves : elles produisent un rapport factuel marqué `failed`, sans publier les conclusions IA rejetées.

## Démarrer et vérifier

Depuis la racine du dépôt, Docker Compose doit être disponible :

```sh
make ollama-start
make ollama-status
# Attendre que qwen2.5:1.5b apparaisse dans la liste.
make verify-report
```

`ollama-start` démarre uniquement Ollama et le téléchargement du modèle. Le téléchargement initial représente plusieurs Go ; les modèles restent dans le volume `ollama_data`. L’API est publiée sur `127.0.0.1:11434`, pas sur toutes les interfaces. Le service `cti-verify` s’exécute sans privilèges root, avec UID/GID 1000 par défaut ; `LOCAL_UID` et `LOCAL_GID` permettent d’adapter ces identifiants.

La vérification collecte exclusivement les trois nouveaux jeux structurés, avec HTTPS, allowlist, robots.txt, limites de taille et YARA. Elle n’appelle ni l’orchestrateur ni MongoDB ni SMTP. La commande `make verify-report` attend automatiquement que le modèle ait été téléchargé. Elle retourne un code non nul si une source n’apporte aucune donnée ou si la synthèse IA échoue aux contrôles.

Résultats : `srcs/requirements/app/reports/verification/rapport_ia.md`, `rapport_ia.quality.json`, `results.json`, `technical.md`, `iocs.csv`, et archives sous `runs/<run_id>/`. Les données sources décodées et scannées sont conservées sous `raw/` avec empreinte dans `results.json`.

Pour la stack complète, préparer `.env` à partir de `.env.example` et renseigner les paramètres réellement nécessaires. La collecte générale conserve ses contrôles d’environnement ; `make verify-report` n’exige aucun secret. Le rapport IA n’est pas envoyé automatiquement par ce script.

## Choisir le serveur et le modèle

| Variable | Valeur par défaut | Rôle |
| --- | --- | --- |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Modèle téléchargé par `ollama-init` et utilisé par la génération |
| `OLLAMA_HOST` | `http://ollama:11434` dans Compose | URL du serveur ; hors Docker, défaut `http://127.0.0.1:11434` |
| `OLLAMA_TIMEOUT` | `180` | Délai de lecture HTTP maximal en secondes |
| `OLLAMA_NUM_CTX` | `4096` | Fenêtre de contexte |
| `OLLAMA_NUM_PREDICT` | `1024` | Budget de sortie |
| `OLLAMA_TEMPERATURE` | `0` | Réduction de la variabilité ; ne garantit pas l’identité des réponses |

Le modèle par défaut occupe environ 1 Go sur disque ; le service limite le chargement à un modèle et une génération simultanés pour les machines modestes. `OLLAMA_NUM_THREAD` permet de régler les threads CPU (2 par défaut). Un modèle plus grand peut être sélectionné avec `OLLAMA_MODEL` si la mémoire disponible le permet.

Le fournisseur refuse les redirections HTTP et les credentials intégrés à l’URL. Il ne bascule pas automatiquement vers Mistral ou un autre fournisseur externe. Le client CLI historique `scripts/ollama_llm.py` reste disponible ; le mode par défaut passe directement par `OllamaProvider` pour conserver les métadonnées et vérifier la sortie structurée.

## Sources et valeur analytique

| Source | Format et usage | Bornes actuelles |
| --- | --- | --- |
| [CISA KEV, miroir officiel](https://github.com/cisagov/kev-data) | CSV : CVE, produit, description, date d’ajout, action requise, usage ransomware connu | 200 lignes, date d’ajout décroissante |
| [Feodo Tracker](https://feodotracker.abuse.ch/blocklist/) | CSV : IP/port de C2, malware, statut publié et dernière observation | 100 lignes maximum, date de dernière activité décroissante |
| [MITRE ATT&CK](https://attack.mitre.org/resources/attack-data-and-tools/) | STIX JSON : techniques actives du référentiel, tactiques, plateformes, identifiants | 64 Mio au téléchargement, descriptions de 1 000 caractères ; objets révoqués/dépréciés exclus |

Ces sources complètent les flux CERT/RSS/API existants. KEV décrit une exploitation rapportée d’une vulnérabilité, pas une vulnérabilité démontrée sur vos machines. Feodo peut contenir des observations anciennes : les entrées de plus de 30 jours sont marquées `historical_activity`, même si leur statut publié est `online`. ATT&CK est un référentiel de comportements, pas une liste d’attaques récentes.

Les types d’attaque sont classés par une table de motifs dans `tools/reporting/threat_evidence.py` : hameçonnage, rançongiciel, déni de service, vol d’identifiants, exécution de code, injection SQL, élévation de privilèges, exfiltration, chaîne d’approvisionnement et C2. Les mentions lexicales ne prouvent pas un incident ; les négations, citations et contextes restent à examiner. Le champ KEV `knownRansomwareCampaignUse=Unknown` n’est pas compté comme usage ransomware connu. Les techniques MITRE conservent leurs tactiques officielles, sans attribuer un identifiant MITRE à partir d’un simple mot-clé.

L’export `attack_types.csv` conserve un identifiant de preuve, la source, la nature référence/renseignement publié, les dates, catégories, CVE/MITRE et actions prescrites lorsqu’elles existent. Les cellules sont protégées contre l’interprétation comme formules. Les comptages portent sur des extraits, pas sur des incidents uniques ou la fréquence réelle des attaques.

Le cache est rafraîchi après 900 secondes par défaut ; le mode offline permet la relecture historique. Le quota global de 100 Mo inclut le référentiel ATT&CK. Les sources structurées sont placées avant les crawls HTML pour éviter que ceux-ci épuisent le quota avant leur acquisition.

## Ajouter un CSV

Ajouter son domaine à `network.allow_domains`, une source `type: csv` dans `sources.yaml`, puis une configuration par source :

```yaml
data_scraper:
  per_source:
    NOM-SOURCE:
      csv:
        record_format: json
        comment_prefix: "#"
        select_columns: [identifier, description, date, action]
        sort_by: date
        descending: true
        max_rows: 100
```

Les dates triées doivent être dans un format lexical compatible, par exemple ISO 8601. Les CSV standard conservent leur comportement historique si `record_format` n’est pas défini. Les sources nécessitant une authentification ne doivent pas être ajoutées avec un faux token. L’ajout d’un dataset ne transforme pas automatiquement ses colonnes en une nouvelle sémantique CTI : compléter les règles d’interprétation et leurs tests si nécessaire.

## Ce que les contrôles garantissent

L’[API de génération Ollama](https://docs.ollama.com/api/generate) reçoit un schéma JSON et une sélection de preuves réparties entre sources. Le modèle choisit uniquement des identifiants de preuves et des codes d’action. Le programme vérifie la compatibilité de chaque action avec la nature et la fraîcheur de la preuve, puis produit une synthèse française déterministe. Les citations sont copiées directement depuis ces preuves par le programme, sans demander au modèle de les retranscrire. Le fournisseur vérifie :

- fin de génération effective avec `done=true` et `done_reason=stop` ;
- 1 à 3 décisions ayant exactement les champs attendus, sans preuve répétée ;
- action compatible avec la preuve : exposition pour KEV, chasse rétrospective pour les indicateurs anciens, couverture de détection pour les références ATT&CK ;
- identifiant de preuve connu, citation exacte de 20 caractères minimum ;
- CVE, identifiants de techniques et URL/IPv4 présents dans la preuve associée ;
- détection heuristique des sorties manifestement non traduites en français ;
- absence de publication de la synthèse rejetée comme une synthèse validée.

`passed` signifie que ces contrôles automatisés réussissent. Il ne certifie ni la justesse sémantique de toute interprétation, ni l’applicabilité des recommandations, ni une conformité ISO, NIS2 ou autre. La disponibilité et la fraîcheur des sources sont documentées séparément. Le choix et l’ordre proposés par le modèle peuvent rester discutables ; le rendu déterministe ne vérifie pas la vérité des sources ni l’exposition de vos actifs. Une revue humaine reste nécessaire.

Les règles YARA de macros et de scripts sont limitées aux formats Office/VBA et markup correspondants pour éviter de rejeter un document JSON qui décrit ces attaques. Les signatures restent des contrôles heuristiques, pas une preuve d’innocuité ; les tests vérifient les cas de données CTI et les formats suspects retenus.

## Rejouer un rapport

Chaque run conserve `request.json`, `response.json` si reçue, `evidence.json`, `attack_types.csv`, `report.md` et `quality.json`. Ce dernier contient les paramètres, l’empreinte du prompt, les empreintes du rapport et des preuves, les métadonnées de génération et le digest du modèle lorsque disponible.

Pour relancer Ollama sur les mêmes résultats sans recontacter les sources :

```sh
docker compose -f srcs/docker-compose.yml run --rm --no-deps cti-verify \
  python scripts/verify_cti_report.py \
  --results reports/verification/results.json \
  --output-dir reports/verification/replay
```

Un nouvel appel au modèle reste une nouvelle génération. Pour reproduire exactement la réponse précédente, consulter la réponse archivée avec son rapport. Les archives de rapports ne sont pas incluses dans l’image Docker ni suivies par Git ; appliquer une politique de rétention adaptée.

## Vérification du 26 novembre 2026

La collecte de vérification a récupéré 200 lignes KEV, 5 entrées Feodo et 706 techniques ATT&CK, soit 911 éléments. Le run `20261126T083307Z-f0e1089c` a présenté 6 preuves au modèle `qwen2.5:1.5b` et retenu 3 décisions compatibles : deux vérifications d’exposition KEV et une recherche historique Feodo. La génération a pris environ 80 secondes sur cette machine de 4 Go de RAM.

Les contrôles automatiques ont réussi ; la relecture a confirmé une rédaction française déterministe et la distinction entre activité historique et référence. Les empreintes du rapport courant, du rapport archivé et des preuves ont été recalculées avec succès. La suite complète dans le conteneur avec les dépendances verrouillées a donné **202 tests réussis**. Ces résultats concernent cet état du code et ce jeu de données ; les flux publics évoluent.

Le modèle 3B initial dépassait le délai disponible, et la rédaction libre du petit modèle n’était pas suffisamment fiable. Le mode retenu limite donc explicitement Ollama au triage : il ne faut pas présenter le rapport comme une analyse libre de l’intégralité des 911 éléments par le LLM.
