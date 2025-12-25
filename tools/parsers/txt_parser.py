from typing import List
from tools.parsers.text_utils import ensure_text


def parse_txt(content: str, conf: dict) -> List[str]:
    text = ensure_text(content, encoding=conf.get("encoding"))
    return [text] if text else []
