"""Fernet encryption for storing API keys at rest."""

from __future__ import annotations

import logging

from cryptography.fernet import Fernet, InvalidToken

from vigil_server.config import settings

logger = logging.getLogger("vigil_server.services.encryption")


def _get_fernet() -> Fernet:
    """Return a Fernet instance using the configured encryption key."""
    key = settings.encryption_key
    if not key:
        raise RuntimeError(
            "VIGIL_ENCRYPTION_KEY is not set. "
            "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string and return the ciphertext as a string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string and return the plaintext."""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        logger.error("Failed to decrypt value — key may have changed")
        raise ValueError("Decryption failed — encryption key may have changed") from exc


def mask_key(key: str) -> str:
    """Mask an API key for display, e.g. 'sk-abc...xyz' -> 'sk-abc****'."""
    if not key or len(key) < 8:
        return "****"
    return key[:6] + "****"
