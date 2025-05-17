from django.db import models


class Feedback(models.Model):
    """
    Very small model just so we have something to store
    after the BFEFormWidget validates.
    """
    name    = models.CharField(max_length=120)
    email   = models.EmailField()
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} – {self.email[:30]}"


class DataForFiltering(models.Model):
    name = models.CharField(max_length=120)
    domain = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    account_credits = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"{self.name} – ${self.account_credits[:30]}"
