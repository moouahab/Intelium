"""
Sanitisation légère des contenus HTML/XML.
Objectif : enlever scripts/style/commentaires et normaliser le texte pour limiter
les surprises lors de la réutilisation ou du reporting.
"""
from __future__ import annotations

from bs4 import BeautifulSoup, Comment


def sanitize_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Supprime scripts/styles/comments
    for tag in soup(["script", "style"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # Retourne le markup nettoyé (structure conservée)
    return str(soup)


def sanitize_xml(xml: str) -> str:
    soup = BeautifulSoup(xml, "xml")
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # retire scripts dans les flux xml/atom/rss
    for tag in soup.find_all("script"):
        tag.decompose()
    return str(soup)
