from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urljoin
import warnings

# Supprime les warnings bs4 quand un contenu XML est parsé via le parser HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def extract_links(html_content: str, base_url: str):
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        links.add(urljoin(base_url, tag["href"]))
    for tag in soup.find_all("script", src=True):
        links.add(urljoin(base_url, tag["src"]))
    return links
