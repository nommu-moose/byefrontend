"""
do not use - broken right now, this has been left in to show intent
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group
from .crypto import derive_key_from_password, encrypt_with_key, decrypt_with_key, generate_secret_key
import os

"""
class EncryptedUnlockKey(models.Model):
    # For key rotation, maybe multiple keys over time, possible need for is_active or version fields
    name = models.CharField(max_length=255, unique=True)

    salt = models.BinaryField(max_length=32)
    # encrypted with a password-derived key.
    encrypted_key = models.BinaryField()  # 24-byte nonce + ciphertext

    objects = models.Manager()

    # Access control:
    # Limit which users or groups can access this key.
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    allowed_groups = models.ManyToManyField(Group, blank=True)

    # For rotation/tracking:
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_key(self, plaintext_key: bytes, password: str):
        \"""Encrypt and store the EUK.\"""
        self.salt = os.urandom(16)
        key = derive_key_from_password(password, self.salt)
        self.encrypted_key = encrypt_with_key(key, plaintext_key)

    def unlock_key(self, password: str) -> bytes:
        \"""Given a password, return the decrypted unlock key.\"""
        key = derive_key_from_password(password, self.salt)
        return decrypt_with_key(key, self.encrypted_key)


class EncryptedSecret(models.Model):
    unlock_key = models.ForeignKey(EncryptedUnlockKey, on_delete=models.CASCADE, related_name="secrets")
    encrypted_value = models.BinaryField()  # The ciphertext for the secret data
    created_at = models.DateTimeField(auto_now_add=True)

    def encrypt_secret(self, unlock_key: bytes, plaintext: bytes):
        self.encrypted_value = encrypt_with_key(unlock_key, plaintext)

    def decrypt_secret(self, unlock_key: bytes) -> bytes:
        return decrypt_with_key(unlock_key, self.encrypted_value)
"""
