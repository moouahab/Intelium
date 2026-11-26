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

    # Index each normalized term once, retaining its category and spelling.
    # This avoids rescanning every text for terms shared across categories.
    terms: dict[str, set[tuple[str, str]]] = {}
    for category, words in keywords.items():
        for word in words or []:
            needle = (word or "").strip()
            if needle:
                terms.setdefault(needle.lower(), set()).add((category, needle))

    found_by_category: dict[str, set[str]] = {}
    for term, destinations in terms.items():
        if any(term in text for text in texts):
            for category, spelling in destinations:
                found_by_category.setdefault(category, set()).add(spelling)
    return {category: sorted(found_by_category[category])
            for category in keywords if category in found_by_category}
