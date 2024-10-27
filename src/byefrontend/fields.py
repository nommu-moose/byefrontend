from django.db import models
from .widgets import SecretToggleCharWidget
from cryptography.fernet import Fernet
import base64

# Encryption key generation - you should securely store and retrieve this key
SECRET_KEY = base64.urlsafe_b64encode(b'my_secret_key_1234567890123456')  # Example; use a secure key
cipher = Fernet(SECRET_KEY)


class SecretCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 15)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # Set the widget to PhoneNumberInput
        kwargs['widget'] = SecretToggleCharWidget
        return super().formfield(**kwargs)

    def get_prep_value(self, value):
        """Encrypt the data before saving to the database."""
        if value is not None:
            # Encrypt the value and encode it for storage
            encrypted_value = cipher.encrypt(value.encode())
            return encrypted_value.decode('utf-8')
        return value

    def from_db_value(self, value, expression, connection):
        """Decrypt the data when retrieving it from the database."""
        if value is not None:
            # Decrypt the value
            decrypted_value = cipher.decrypt(value.encode())
            return decrypted_value.decode('utf-8')
        return value
