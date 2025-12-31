import threading


class Quota:
    """Quota global (pages/bytes) thread-safe."""

    def __init__(self, max_pages: int | None = None, max_bytes: int | None = None):
        self.max_pages = max_pages
        self.max_bytes = max_bytes
        self.pages_used = 0
        self.bytes_used = 0
        self._lock = threading.Lock()

    def reserve_page(self) -> bool:
        """Réserve une page si quota non dépassé. Retourne False sinon."""
        with self._lock:
            if self.max_pages is not None and self.pages_used >= self.max_pages:
                return False
            self.pages_used += 1
            return True

    def add_bytes(self, size: int | None) -> bool:
        """Ajoute des octets et retourne False si le quota est dépassé après ajout."""
        if size is None:
            return True
        with self._lock:
            self.bytes_used += size
            if self.max_bytes is not None and self.bytes_used > self.max_bytes:
                return False
            return True

    def remaining_pages(self) -> int | None:
        if self.max_pages is None:
            return None
        with self._lock:
            return max(0, self.max_pages - self.pages_used)

    def remaining_bytes(self) -> int | None:
        if self.max_bytes is None:
            return None
        with self._lock:
            return max(0, self.max_bytes - self.bytes_used)
