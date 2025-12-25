from __future__ import annotations

import json
import csv
from io import StringIO
from typing import Any, List, Optional


def ensure_text(content: Any, encoding: Optional[str] = None) -> str:
    """
    Normalise en chaîne de caractères.
    - bytes -> décodage (utf-8 par défaut, fallback latin-1)
    - autres -> str(...) + normalisation des sauts de ligne
    """
    if isinstance(content, bytes):
        try:
            text = content.decode(encoding or "utf-8", errors="replace")
        except Exception:
            text = content.decode("latin-1", errors="replace")
    else:
        text = str(content)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def safe_json_load(content: Any, encoding: Optional[str] = None) -> Any:
    text = ensure_text(content, encoding=encoding)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def safe_csv_rows(content: Any, delimiter: str = ",", encoding: Optional[str] = None) -> List[List[str]]:
    text = ensure_text(content, encoding=encoding)
    reader = csv.reader(StringIO(text), delimiter=delimiter)
    try:
        return list(reader)
    except csv.Error:
        return []
