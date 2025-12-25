from typing import List
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

# Supprime les warnings bs4 quand un contenu XML est parsé via le parser HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def parse_html(content: str, conf: dict) -> List[str]:
    extract_rules = conf.get("extract", [])
    include_attributes = conf.get("include_attributes", [])
    soup = BeautifulSoup(content, "html.parser")
    results: List[str] = []
    if not extract_rules:
        return [soup.get_text(" ", strip=True)]
    for rule in extract_rules:
        tag = rule.get("tag")
        attrs = rule.get("attrs", {}) if isinstance(rule.get("attrs", {}), dict) else {}
        for node in soup.find_all(tag, attrs=attrs):
            parts = [node.get_text(" ", strip=True)]
            for attr in include_attributes:
                if node.has_attr(attr):
                    parts.append(f"{attr}={node[attr]}")
            results.append(" | ".join(parts))
    return results
