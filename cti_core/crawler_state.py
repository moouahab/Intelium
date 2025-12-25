from collections import deque
from typing import Set
import threading
import contextlib
from .Source import Source


class CrawlerState:
    """Gère la frontier (queue) et les visites pour le crawl."""

    def __init__(self, max_depth: int, max_pages: int | None, normalizer, thread_safe: bool = False):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._normalizer = normalizer
        self.queue = deque()
        self.visited: Set[str] = set()
        self.pages_processed = 0
        self._thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None

    def _guard(self):
        if not self._thread_safe or self._lock is None:
            return contextlib.nullcontext()
        return self._lock

    def add(self, source: Source, depth: int) -> None:
        if depth > self.max_depth:
            return
        norm = self._normalizer(source.url)
        with self._guard():
            if norm in self.visited:
                return
            self.queue.append((source, depth))

    def has_next(self) -> bool:
        with self._guard():
            if self.max_pages and self.pages_processed >= self.max_pages:
                return False
            return bool(self.queue)

    def pop(self):
        with self._guard():
            return self.queue.popleft()

    def pop_if_any(self):
        with self._guard():
            if self.max_pages and self.pages_processed >= self.max_pages:
                return None
            if not self.queue:
                return None
            item = self.queue.popleft()
            self.pages_processed += 1
            return item

    def mark_visited(self, url: str) -> None:
        with self._guard():
            self.visited.add(self._normalizer(url))

    def already_visited(self, url: str) -> bool:
        with self._guard():
            return self._normalizer(url) in self.visited
