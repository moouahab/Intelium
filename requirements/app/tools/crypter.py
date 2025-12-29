import hashlib
from pathlib import Path
from cryptography.fernet import Fernet

def compute_sha256(path: str | Path) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_sha256_from_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_sha256_from_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_file(path: str | Path, key: bytes) -> str:
    path = Path(path)
    data = path.read_bytes()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    out_path = f"{path}.enc"
    Path(out_path).write_bytes(encrypted)
    return out_path


def decrypt_file(path: str | Path, key: bytes) -> str:
    path = Path(path)
    data = path.read_bytes()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)
    out_path = f"{path}.dec"
    Path(out_path).write_bytes(decrypted)
    return out_path

def verify_file_integrity(path: str | Path, expected_hash: str) -> bool:
    return compute_sha256(path) == expected_hash
