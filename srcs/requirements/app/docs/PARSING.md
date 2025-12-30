# Extraction / Parsing

## Pipeline
- Les contenus téléchargés passent par `tools/parser.parse_content(type, content, scraping_conf)`.
- La config `data_scraper` (config/scraping.yaml) pilote les options par type.
- Le `Scraper` ajoute les extraits dans `results` (champ `extracted`) et dans le résumé JSON.
- Optionnel : extraction d’IOC (CVE, URLs, IPv4) si `extract_iocs` est activé pour le type ou la source.
- Optionnel : sanitation légère des contenus HTML/XML si `sanitize_downloads` (network) ou `sanitize: true` (par type) pour retirer scripts/commentaires avant réutilisation/rapport.

## Règles par type
- **html** : utilise BeautifulSoup si dispo (`pip install beautifulsoup4`), sinon fallback brut.
  - `extract`: liste de tags à extraire (texte).
  - `include_attributes`: attrs à récupérer (href/src/alt…).
- **api** (json) : parse JSON et évalue des chemins simples `$.a.b` ou `$.arr[*].c`.
- **xml** : tags listés dans `extract_tags`, concatène le texte.
- **csv** : `delimiter`, `has_header`, `select_columns` (par nom si header).
- **pdf** : extraction texte via pdfplumber (page par page). Options : `extract_text` (on/off), `max_pages`, `max_chars` (tronque chaque page), `keep_images` (ajoute une ligne descriptive par image intégrée). Retourne une liste vide si pdfplumber est absent ou en cas d’erreur.
- **image** : OCR via pytesseract + Pillow. Options : `ocr` (on/off), `languages` (str ou liste → `eng+fra`), `max_chars`, `errors` (`log|warn|ignore`). Tesseract manquant ou erreur OCR → liste vide (warning loggable).
- **txt** : retourne le texte brut.

## Rapport
- Généré via `tools/report.py` (markdown ou json selon `output.format`, fichier `output.file`).
- Contient statut, chemin enregistré, extraits (limités) par source.
