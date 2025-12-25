from typing import List
from tools.parsers.text_utils import safe_csv_rows


def parse_csv(content: str, conf: dict) -> List[str]:
    delimiter = conf.get("delimiter", ",")
    has_header = conf.get("has_header", True)
    select_columns = conf.get("select_columns", [])
    results: List[str] = []
    rows = safe_csv_rows(content, delimiter=delimiter, encoding=conf.get("encoding"))
    if not rows:
        return results
    start_idx = 1 if has_header else 0
    headers = rows[0] if has_header else []
    for row in rows[start_idx:]:
        if select_columns and headers:
            items = [row[headers.index(col)] for col in select_columns if col in headers and headers.index(col) < len(row)]
            if items:
                results.append(", ".join(items))
        else:
            results.append(", ".join(row))
    return results
