# tests/test_crypter.py
import os
import tempfile
from tools import crypter

def test_hash_consistency():
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write("test data")
        tmp_path = tmp.name
    hash1 = crypter.compute_sha256(tmp_path)
    hash2 = crypter.compute_sha256(tmp_path)
    assert hash1 == hash2, "Hashes do not match for the same file"
    os.remove(tmp_path)

def test_hash_text():
    text = "important string"
    hash1 = crypter.compute_sha256_from_text(text)
    hash2 = crypter.compute_sha256_from_text(text)
    assert hash1 == hash2

def test_encrypt_decrypt_cycle():
    key = crypter.generate_key()
    content = b"Very secret data that needs encryption."
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    enc_path = crypter.encrypt_file(tmp_path, key)
    dec_path = crypter.decrypt_file(enc_path, key)
    with open(dec_path, "rb") as f:
        decrypted = f.read()
    assert decrypted == content, "Decrypted data doesn't match original"
    os.remove(tmp_path)
    os.remove(enc_path)
    if os.path.exists(dec_path):
        os.remove(dec_path)


def test_file_integrity():
    content = "verify me"
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write(content)
        path = tmp.name
    h = crypter.compute_sha256(path)
    assert crypter.verify_file_integrity(path, h)
    os.remove(path)
