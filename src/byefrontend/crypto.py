import os
import base64
from argon2.low_level import hash_secret_raw, Type
from nacl.bindings import (
    crypto_aead_xchacha20poly1305_ietf_encrypt,
    crypto_aead_xchacha20poly1305_ietf_decrypt
)

ARGON2_TIME_COST = 4
ARGON2_MEMORY_COST = 102400
ARGON2_PARALLELISM = 2
ARGON2_HASH_LEN = 32


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive a key from a password using Argon2.
    Returns a 32-byte key suitable for XChaCha20-Poly1305."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    key = hash_secret_raw(
        password, salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=Type.ID
    )
    return key


def encrypt_with_key(key: bytes, plaintext: bytes, aad: bytes = b'') -> bytes:
    """Encrypt plaintext with XChaCha20-Poly1305 using the given key."""
    nonce = os.urandom(24)
    ciphertext = crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, aad, nonce, key)
    return nonce + ciphertext


def decrypt_with_key(key: bytes, ciphertext: bytes, aad: bytes = b'') -> bytes:
    """Decrypt ciphertext with XChaCha20-Poly1305 using the given key."""
    nonce = ciphertext[:24]
    enc = ciphertext[24:]
    return crypto_aead_xchacha20poly1305_ietf_decrypt(enc, aad, nonce, key)


def generate_secret_key() -> bytes:
    """Generate a new 32-byte XChaCha20-Poly1305 key."""
    return os.urandom(32)
