from typing import List, Optional
from bs4 import BeautifulSoup


def parse_xml(content: str, conf: dict) -> List[str]:
    """
    Extrait le texte des tags demandés. Compatibilité : supporte la clé
    historique `tags` et la clé `extract_tags` utilisée dans scraping.yaml.
    """
    raw_tags = conf.get("tags") or conf.get("extract_tags") or []

    def _name(entry) -> Optional[str]:
        if isinstance(entry, str):
            return entry
        if isinstance(entry, dict):
            return entry.get("tag") or entry.get("name")
        return None

    tags = [_name(entry) for entry in raw_tags]
    tags = [t for t in tags if t]
    soup = BeautifulSoup(content, "xml")
    results: List[str] = []
    if not tags:
        return [content]
    for tag in tags:
        for node in soup.find_all(tag):
            text = node.get_text(strip=True)
            if text:
                results.append(text)
    return results
