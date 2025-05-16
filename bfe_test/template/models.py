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
