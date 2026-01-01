from typing import Any, Dict, Optional
from pathlib import Path
import hashlib
from tools.crypter import compute_sha256_from_text
from tools.providers.http.download import download_source
from tools.providers.http.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.config.overrides import normalize_overrides


class Source:
    """
        Représente une source d'information (site web, API, etc.)

        Attributs :
        - name : Nom de la source
        - url : URL de la source
        - type : Type de la source (html, api, etc.)
        - hash : Hash SHA-256 du contenu, pour vérifier les changements
        - date : Date connue de la source
        - content : Contenu extrait (texte brut)
        - status : État actuel (pending, downloaded, error)
        - error : Message d'erreur éventuel
    """

    def __init__(self, source: Dict):
        self.name: Optional[str] = source.get("name")
        self.url: str = source.get("url", "")
        self.type: str = source.get("type", "html")
        self.hash: Optional[str] = source.get("hash")
        self.date: Optional[str] = source.get("date")
        self.content: Optional[Any] = None
        self.status: str = "pending"
        self.error: Optional[str] = None
        self.overrides: dict = normalize_overrides(source.get("overrides", {}))

    def _compute_hash_from_content(self, content: Any) -> Optional[str]:
        """Calcule un hash SHA-256 pour du texte ou des bytes."""
        if content is None:
            return None
        if isinstance(content, str):
            return compute_sha256_from_text(content)
        if isinstance(content, (bytes, bytearray)):
            return hashlib.sha256(content).hexdigest()
        return None

    def normalized_overrides(self) -> dict:
        """Retourne les overrides normalisés."""
        return normalize_overrides(self.overrides)

    def download_manager(
        self,
        policy: Optional[NetworkPolicy] = None,
        storage: Optional[StorageTarget] = None,
        headers: Optional[dict] = None,
    ) -> DownloadResult:
        """
        Gestionnaire générique qui délègue le téléchargement selon le type de source.
        Supporte html, api, xml, pdf, csv, image, ignore.
        """
        if storage is None:
            storage = StorageTarget(
                base_dir=Path("docs"),
                theme=self.type or "misc",
                name=self.name or "source",
            )
        result = download_source(
            {"url": self.url, "type": self.type, "name": self.name},
            policy=policy,
            storage=storage,
            headers=headers,
        )
        self.status = result.status
        self.error = result.error
        if result.status == "downloaded":
            self.content = result.content
            self.update_hash()
        elif result.status == "skipped":
            self.content = None
            self.hash = None
        return result

    def update_hash(self):
        """Met à jour le hash à partir du contenu actuel."""
        if self.content is None:
            self.hash = None
            return
        computed = self._compute_hash_from_content(self.content)
        self.hash = computed

    def has_changed(self, previous_hash: Optional[str]) -> bool:
        """Compare le hash actuel avec un ancien pour détecter les changements."""
        if self.content is None:
            return False
        current = self._compute_hash_from_content(self.content)
        if current is None:
            return False
        return current != previous_hash

    def verify_integrity(self) -> bool:
        """Vérifie si le hash enregistré correspond au contenu actuel."""
        if not self.hash or self.content is None:
            return False
        current = self._compute_hash_from_content(self.content)
        if current is None:
            return False
        return current == self.hash
