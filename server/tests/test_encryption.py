"""Tests for encryption service."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet


@pytest.fixture(autouse=True)
def _set_encryption_key():
    """Set a test encryption key."""
    key = Fernet.generate_key().decode()
    with patch("vigil_server.services.encryption.settings") as mock_settings:
        mock_settings.encryption_key = key
        yield


def test_encrypt_decrypt():
    from vigil_server.services.encryption import decrypt, encrypt

    plaintext = "sk-test-key-12345"
    ciphertext = encrypt(plaintext)
    assert ciphertext != plaintext
    assert decrypt(ciphertext) == plaintext


def test_encrypt_produces_different_ciphertexts():
    from vigil_server.services.encryption import encrypt

    ct1 = encrypt("same-key")
    ct2 = encrypt("same-key")
    # Fernet uses random IVs so ciphertexts should differ
    assert ct1 != ct2


def test_decrypt_with_wrong_key_fails():
    from vigil_server.services.encryption import encrypt

    ciphertext = encrypt("secret")

    other_key = Fernet.generate_key().decode()
    with patch("vigil_server.services.encryption.settings") as mock_settings:
        mock_settings.encryption_key = other_key
        from vigil_server.services.encryption import decrypt

        with pytest.raises(ValueError, match="Decryption failed"):
            decrypt(ciphertext)


def test_mask_key():
    from vigil_server.services.encryption import mask_key

    assert mask_key("sk-proj-abc123xyz") == "sk-pro****"
    assert mask_key("short") == "****"
    assert mask_key("") == "****"


def test_missing_encryption_key_raises():
    with patch("vigil_server.services.encryption.settings") as mock_settings:
        mock_settings.encryption_key = ""
        from vigil_server.services.encryption import encrypt

        with pytest.raises(RuntimeError, match="VIGIL_ENCRYPTION_KEY is not set"):
            encrypt("test")
