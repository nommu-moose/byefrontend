"""
BFE Model Views - Declarative model-to-widget view generation.

Similar to Django admin, but with full byefrontend widget rendering.

Usage:
    from byefrontend.model_views import bfe, BFEModelView

    @bfe.register(MyModel)
    class MyModelView(BFEModelView):
        list_fields = ('name', 'email', 'created')
        ...

    # In urls.py:
    urlpatterns = [
        path('bfe/', include(bfe.urls)),
    ]
"""
from __future__ import annotations

from importlib import import_module

from .base import BFEModelView
from .registry import bfe, BFEViewRegistry
from .field_mapping import config_for_field, configs_for_model


def autodiscover():
    """
    Import all `bfe_views.py` files from installed apps,
    similar to Django admin's autodiscover().
    
    Call this in your root URLconf or AppConfig.ready().
    Safe to call before Django is fully configured - will be a no-op.
    """
    from django.apps import apps
    
    # Check if apps are ready before attempting to autodiscover
    if not apps.ready:
        return
    
    for app_config in apps.get_app_configs():
        try:
            import_module(f'{app_config.name}.bfe_views')
        except ImportError:
            # No bfe_views module in this app - that's fine
            pass


__all__ = (
    'BFEModelView',
    'BFEViewRegistry',
    'bfe',
    'autodiscover',
    'config_for_field',
    'configs_for_model',
)

