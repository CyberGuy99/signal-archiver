from __future__ import annotations

import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


NONCE_SIZE = 12


def derive_key(password: str) -> bytes:
    """Derive a 256-bit key from a password using SHA256."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data with AES-GCM and return nonce + ciphertext_with_tag."""
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_data(blob: bytes, key: bytes) -> bytes:
    """Decrypt nonce + ciphertext_with_tag from encrypt_data."""
    if len(blob) <= NONCE_SIZE:
        raise ValueError("Encrypted payload is too short")

    nonce = blob[:NONCE_SIZE]
    ciphertext = blob[NONCE_SIZE:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
