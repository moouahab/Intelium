from typing import List
from bs4 import BeautifulSoup


def parse_xml(content: str, conf: dict) -> List[str]:
    tags = conf.get("tags", [])
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
