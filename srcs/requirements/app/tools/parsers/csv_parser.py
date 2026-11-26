from typing import List
import json
from tools.parsers.text_utils import safe_csv_rows


def parse_csv(content: str, conf: dict) -> List[str]:
    delimiter = conf.get("delimiter", ",")
    has_header = conf.get("has_header", True)
    select_columns = conf.get("select_columns", [])
    results: List[str] = []
    rows = safe_csv_rows(content, delimiter=delimiter, encoding=conf.get("encoding"))
    # Commented feeds such as Feodo publish metadata before the actual CSV header.
    prefix = conf.get("comment_prefix")
    if prefix:
        rows = [row for row in rows if row and not row[0].lstrip().startswith(prefix)]
    if not rows:
        return results
    start_idx = 1 if has_header else 0
    headers = rows[0] if has_header else []
    headers = [header.lstrip("\ufeff").strip() for header in headers]
    positions = {header: index for index, header in reversed(list(enumerate(headers)))}
    selected = [positions[col] for col in select_columns if col in positions]
    data_rows = rows[start_idx:]
    sort_column = conf.get("sort_by")
    if sort_column in positions:
        column = positions[sort_column]
        data_rows = sorted(data_rows, key=lambda row: row[column] if column < len(row) else "", reverse=bool(conf.get("descending", False)))
    limit = conf.get("max_rows")
    if isinstance(limit, int) and limit >= 0:
        data_rows = data_rows[:limit]
    for row in data_rows:
        if conf.get("record_format") == "json" and headers:
            columns = selected if select_columns else range(len(headers))
            record = {headers[index]: row[index] for index in columns if index < len(row)}
            if record:
                results.append(json.dumps(record, ensure_ascii=False))
            continue
        if select_columns and headers:
            items = [row[index] for index in selected if index < len(row)]
            if items:
                results.append(", ".join(items))
        else:
            results.append(", ".join(row))
    return results
