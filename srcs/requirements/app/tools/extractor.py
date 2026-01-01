from __future__ import annotations
from typing import Any, Tuple
import tools.parser as parser
from tools.parsers.text_utils import ensure_text
from tools.keywords import find_keyword_hits


class Extractor:
    """
    Centralise l'extraction des contenus et le matching des mots-clés.
    Permet d'injecter un extracteur custom dans le Scraper pour tests/extensions.
    """

    def __init__(self, scraping_settings: dict, keywords: dict | None = None):
        self.scraping_settings = scraping_settings or {}
        self.keywords = keywords or {}

    def extract(self, source_type: str, content: Any, source_name: str | None = None) -> Tuple[list[str], dict]:
        try:
            extracted = parser.parse_content(
                source_type,
                content,
                self.scraping_settings,
                source_name=source_name,
            ) or []
        except Exception:
            extracted = []
        texts_for_match = list(extracted)
        raw_text = ensure_text(content) if content is not None else ""
        if raw_text:
            texts_for_match.append(raw_text)
        keyword_hits = find_keyword_hits(texts_for_match, self.keywords)
        return extracted, keyword_hits
