from django.db import models
from .models import EncryptedUnlockKey, EncryptedSecret
from .crypto import generate_secret_key


class EncryptedTextField(models.BinaryField):
    description = "An encrypted text field using XChaCha20-Poly1305"

    """
    Note: Decryption and encryption is handled by the model’s methods (encrypt_secret, decrypt_secret)
      rather than directly in the field so that you can control the context and key availability.
    """

    def from_db_value(self, value, expression, connection):
        # Raw ciphertext from DB, just return it as is. Decryption is handled externally.
        return value

    def to_python(self, value):
        # if string, assume ciphertext. Decryption handled by model methods.
        return value

    def get_prep_value(self, value):
        # Value should already be ciphertext (bytes)
        return value


def rotate_key(old_key_id: int, password: str, new_key_name: str):
    old_euk = EncryptedUnlockKey.objects.get(id=old_key_id, is_active=True)
    # Unlock old key:
    old_unlock_key = old_euk.unlock_key(password)

    # Create new key:
    new_unlock_key = generate_secret_key()
    new_euk = EncryptedUnlockKey.objects.create(
        name=new_key_name,
        is_active=True
    )
    new_euk.set_key(new_unlock_key, password)
    new_euk.save()

    # Re-encrypt all EncryptedSecrets:
    secrets = old_euk.secrets.all()
    for secret in secrets:
        plaintext = secret.decrypt_secret(old_unlock_key)
        secret.encrypt_secret(new_unlock_key, plaintext)
        secret.unlock_key = new_euk
        secret.save()

    # Mark old EUK as inactive:
    old_euk.is_active = False
    old_euk.save()

    return new_euk
