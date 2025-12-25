# Extraction / Parsing

## Pipeline
- Les contenus téléchargés passent par `tools/parser.parse_content(type, content, scraping_conf)`.
- La config `data_scraper` (config/scraping.yaml) pilote les options par type.
- Le `Scraper` ajoute les extraits dans `results` (champ `extracted`) et dans le résumé JSON.

## Règles par type
- **html** : utilise BeautifulSoup si dispo (`pip install beautifulsoup4`), sinon fallback brut.
  - `extract`: liste de tags à extraire (texte).
  - `include_attributes`: attrs à récupérer (href/src/alt…).
- **api** (json) : parse JSON et évalue des chemins simples `$.a.b` ou `$.arr[*].c`.
- **xml** : tags listés dans `extract_tags`, concatène le texte.
- **csv** : `delimiter`, `has_header`, `select_columns` (par nom si header).
- **pdf** : placeholder (non implémenté).
- **image** : placeholder OCR (non implémenté).
- **txt** : retourne le texte brut.

## Rapport
- Généré via `tools/report.py` (markdown ou json selon `output.format`, fichier `output.file`).
- Contient statut, chemin enregistré, extraits (limités) par source.
