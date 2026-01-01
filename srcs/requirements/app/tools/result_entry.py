from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator
from collections.abc import MutableMapping


_CORE_FIELDS = {
    "url",
    "name",
    "type",
    "status",
    "error",
    "saved_path",
    "extracted",
    "keywords",
    "confidence",
}


@dataclass
class ResultEntry(MutableMapping[str, Any]):
    url: str
    name: str | None
    type: str | None
    status: str
    error: str | None = None
    saved_path: str | None = None
    extracted: list[Any] = field(default_factory=list)
    keywords: dict | None = None
    confidence: float | None = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "url": self.url,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "error": self.error,
            "saved_path": self.saved_path,
            "extracted": self.extracted,
            "confidence": self.confidence,
        }
        if self.keywords:
            data["keywords"] = self.keywords
        data.update(self.extra)
        return data

    def _keys(self) -> list[str]:
        keys = [
            "url",
            "name",
            "type",
            "status",
            "error",
            "saved_path",
            "extracted",
            "confidence",
        ]
        if self.keywords:
            keys.append("keywords")
        keys.extend(self.extra.keys())
        return keys

    def __getitem__(self, key: str) -> Any:
        if key in _CORE_FIELDS:
            if key == "keywords" and not self.keywords:
                raise KeyError(key)
            return getattr(self, key)
        if key in self.extra:
            return self.extra[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key: str, value: Any) -> None:
        if key in _CORE_FIELDS:
            if key == "keywords":
                setattr(self, key, value or None)
            else:
                setattr(self, key, value)
        else:
            self.extra[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.extra:
            del self.extra[key]
            return
        if key == "keywords":
            self.keywords = None
            return
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._keys())

    def __len__(self) -> int:
        return len(self._keys())


def as_dict(result: Any) -> Dict[str, Any]:
    if isinstance(result, ResultEntry):
        return result.to_dict()
    return dict(result) if not isinstance(result, dict) else result


def normalize_results(results: Iterable[Any]) -> list[Dict[str, Any]]:
    return [as_dict(r) for r in results]
