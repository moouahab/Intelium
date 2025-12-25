from typing import List
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
try:
    from lxml import html as lxml_html  # type: ignore
    HAS_LXML = True
except Exception:
    HAS_LXML = False

# Supprime les warnings bs4 quand un contenu XML est parsé via le parser HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def parse_html(content: str, conf: dict) -> List[str]:
    extract_rules = conf.get("extract", [])
    include_attributes = conf.get("include_attributes", [])
    css_selectors = conf.get("css_selectors", [])
    xpath_selectors = conf.get("xpath_selectors", [])
    soup = BeautifulSoup(content, "html.parser")
    results: List[str] = []
    if not extract_rules and not css_selectors and not xpath_selectors:
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
    # CSS selectors
    for selector in css_selectors or []:
        sel = selector.get("selector") if isinstance(selector, dict) else selector
        if not sel:
            continue
        nodes = soup.select(sel)
        for node in nodes:
            parts = [node.get_text(" ", strip=True)]
            attrs = selector.get("include_attributes", include_attributes) if isinstance(selector, dict) else include_attributes
            for attr in attrs:
                if node.has_attr(attr):
                    parts.append(f"{attr}={node[attr]}")
            results.append(" | ".join(parts))
    # XPath selectors (optionnel si lxml dispo)
    if xpath_selectors and HAS_LXML:
        try:
            tree = lxml_html.fromstring(content)
            for xp in xpath_selectors:
                expr = xp.get("path") if isinstance(xp, dict) else xp
                if not expr:
                    continue
                for elem in tree.xpath(expr):
                    try:
                        text = elem.text_content()
                    except Exception:
                        text = str(elem)
                    if text:
                        results.append(text.strip())
        except Exception:
            pass
    return results
