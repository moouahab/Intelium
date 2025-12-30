from typing import Any, List
from tools.parsers.text_utils import safe_json_load

try:
    from jsonpath_ng import parse as jsonpath_parse  # type: ignore
    HAS_JSONPATH = True
except ImportError:
    HAS_JSONPATH = False


def _parse_json_path(path: str, data: Any) -> List[Any]:
    if HAS_JSONPATH:
        try:
            expr = jsonpath_parse(path)
            return [match.value for match in expr.find(data)]
        except Exception:
            return []
    # Fallback simpliste
    if not path.startswith("$."):
        return []
    tokens = path[2:].split(".")

    def recurse(obj: Any, parts: List[str]) -> List[Any]:
        if not parts:
            return [obj]
        head, *tail = parts
        results: List[Any] = []
        if head.endswith("]"):
            name, _, _ = head.partition("[")
            arr = obj.get(name, []) if isinstance(obj, dict) else []
            for item in arr:
                results.extend(recurse(item, tail))
        else:
            next_obj = obj.get(head) if isinstance(obj, dict) else None
            if next_obj is not None:
                results.extend(recurse(next_obj, tail))
        return results

    return recurse(data, tokens)


def parse_json(content: str, conf: dict) -> List[str]:
    data = safe_json_load(content, encoding=conf.get("encoding"))
    if data is None:
        return []
    fields = conf.get("fields", [])
    results: List[str] = []
    if not fields:
        return [content]
    for field in fields:
        path = field.get("path")
        if not path:
            continue
        values = _parse_json_path(path, data)
        for v in values:
            if isinstance(v, (dict, list)):
                results.append(str(v))
            else:
                results.append(str(v))
    return results
