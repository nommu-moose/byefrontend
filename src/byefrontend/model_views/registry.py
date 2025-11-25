"""
BFE View Registry - Registration and URL generation for model views.

Similar to Django's admin.site, this provides a central registry
for model view configurations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.db import models
from django.urls import path, URLPattern

if TYPE_CHECKING:
    from .base import BFEModelView


class BFEViewRegistry:
    """
    Central registry for BFE model views.
    
    Usage:
        from byefrontend.model_views import bfe, BFEModelView
        
        @bfe.register(MyModel)
        class MyModelView(BFEModelView):
            list_fields = ('name', 'email')
        
        # In urls.py:
        urlpatterns = [
            path('bfe/', include(bfe.urls)),
        ]
    """
    
    def __init__(self, name: str = 'bfe'):
        self._registry: dict[Type[models.Model], BFEModelView] = {}
        self.name = name
    
    def register(self, model_class: Type[models.Model], view_class: Type[BFEModelView] | None = None):
        """
        Register a model with an optional view class.
        
        Can be used as a decorator:
            @bfe.register(MyModel)
            class MyModelView(BFEModelView):
                ...
        
        Or directly:
            bfe.register(MyModel, MyModelView)
        """
        def decorator(vc: Type[BFEModelView]) -> Type[BFEModelView]:
            # Instantiate the view class and store it
            instance = vc()
            instance.model = model_class
            self._registry[model_class] = instance
            return vc
        
        if view_class is not None:
            # Direct registration
            instance = view_class()
            instance.model = model_class
            self._registry[model_class] = instance
            return view_class
        
        # Used as decorator
        return decorator
    
    def unregister(self, model_class: Type[models.Model]) -> None:
        """Remove a model from the registry."""
        self._registry.pop(model_class, None)
    
    def is_registered(self, model_class: Type[models.Model]) -> bool:
        """Check if a model is registered."""
        return model_class in self._registry
    
    def get_view(self, model_class: Type[models.Model]) -> BFEModelView | None:
        """Get the view configuration for a model."""
        return self._registry.get(model_class)
    
    def get_urls(self) -> list[URLPattern]:
        """
        Generate URL patterns for all registered models.
        
        URL structure:
            /                             → index (all models)
            /appname/modelname/           → list
            /appname/modelname/<pk>/      → detail
            /appname/modelname/add/       → create
            /appname/modelname/<pk>/edit/ → update
            /appname/modelname/<pk>/delete/ → delete
        
        Automatically triggers autodiscover() if not already done.
        """
        # Ensure bfe_views modules are loaded
        from . import autodiscover
        autodiscover()
        
        from .views import (
            BFEIndexView,
            BFEModelListView,
            BFEModelDetailView,
            BFEModelCreateView,
            BFEModelUpdateView,
            BFEModelDeleteView,
        )
        
        urlpatterns: list[URLPattern] = [
            # Index page showing all registered models
            path('', BFEIndexView.as_view(), name='index'),
        ]
        
        for model_class, model_view in self._registry.items():
            app_label = model_class._meta.app_label
            model_name = model_class._meta.model_name
            prefix = f'{app_label}/{model_name}'
            
            # Generate view classes bound to this model_view
            list_view = BFEModelListView.as_view(
                model=model_class,
                model_view=model_view,
            )
            detail_view = BFEModelDetailView.as_view(
                model=model_class,
                model_view=model_view,
            )
            create_view = BFEModelCreateView.as_view(
                model=model_class,
                model_view=model_view,
            )
            update_view = BFEModelUpdateView.as_view(
                model=model_class,
                model_view=model_view,
            )
            delete_view = BFEModelDeleteView.as_view(
                model=model_class,
                model_view=model_view,
            )
            
            # URL name prefix for reverse()
            name_prefix = f'{app_label}_{model_name}'
            
            urlpatterns.extend([
                path(f'{prefix}/', list_view, name=f'{name_prefix}_list'),
                path(f'{prefix}/<int:pk>/', detail_view, name=f'{name_prefix}_detail'),
                path(f'{prefix}/add/', create_view, name=f'{name_prefix}_create'),
                path(f'{prefix}/<int:pk>/edit/', update_view, name=f'{name_prefix}_update'),
                path(f'{prefix}/<int:pk>/delete/', delete_view, name=f'{name_prefix}_delete'),
            ])
        
        return urlpatterns
    
    @property
    def urls(self):
        """
        Property for easy inclusion in urlpatterns.
        
        Usage:
            path('bfe/', include(bfe.urls))
        
        Returns a 2-tuple (patterns, app_namespace) for Django's include().
        """
        return self.get_urls(), self.name


# Singleton instance - similar to admin.site
bfe = BFEViewRegistry()

