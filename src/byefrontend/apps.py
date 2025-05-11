from django.apps import AppConfig
from django.conf import settings


class ByeFrontendConfig(AppConfig):             # <– pick any name you like
    default_auto_field = "django.db.models.BigAutoField"
    name = "byefrontend"
    verbose_name = "Bye-Frontend Widgets"

    def ready(self) -> None:
        """
        • Register a sane default for the *optional* widget cache flag
        • Useful when the host project forgets to set it.
        """
        if not hasattr(settings, "BFE_WIDGET_CACHE"):
            settings.BFE_WIDGET_CACHE = False
