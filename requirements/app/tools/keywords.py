from __future__ import annotations

from typing import Dict, Iterable, List


def find_keyword_hits(items: Iterable[str], keywords: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Retourne un dictionnaire {categorie: [mots-clés trouvés]} basé sur une recherche
    insensible à la casse dans la liste de textes fournie.
    """
    hits: Dict[str, List[str]] = {}
    texts = [item.lower() for item in items if isinstance(item, str)]
    if not texts or not keywords:
        return hits

    for category, words in keywords.items():
        found = set()
        for word in words or []:
            needle = (word or "").strip()
            if not needle:
                continue
            lower = needle.lower()
            if any(lower in text for text in texts):
                found.add(needle)
        if found:
            hits[category] = sorted(found)
    return hits
