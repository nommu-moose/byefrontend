from django.apps import AppConfig
from django.conf import settings


class ByeFrontendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "byefrontend"
    verbose_name = "Bye-Frontend Widgets"

    def ready(self) -> None:
        """register sane default for the *optional* widget cache flag"""
        # todo: consider more automated settings here
        if not hasattr(settings, "BFE_WIDGET_CACHE"):
            settings.BFE_WIDGET_CACHE = False
