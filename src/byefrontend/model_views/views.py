"""
Auto-generated Django views for BFE Model Views.

These views integrate with Django's generic class-based views
while using BFE widgets for rendering.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from ..render import aggregate_media

if TYPE_CHECKING:
    from .base import BFEModelView


class BFEIndexView(TemplateView):
    """
    Index page showing all registered models with navigation.
    Similar to Django admin's index page.
    """
    template_name = "byefrontend/model_views/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from .registry import bfe
        from . import autodiscover
        autodiscover()
        
        # Build model list with URLs
        models_list = []
        for model_class, model_view in bfe._registry.items():
            app_label = model_class._meta.app_label
            model_name = model_class._meta.model_name
            name_prefix = f"{app_label}_{model_name}"
            
            models_list.append({
                'name': model_class._meta.verbose_name.title(),
                'name_plural': model_class._meta.verbose_name_plural.title(),
                'app_label': app_label,
                'model_name': model_name,
                'list_url': reverse(f'bfe:{name_prefix}_list'),
                'add_url': reverse(f'bfe:{name_prefix}_create'),
                'count': model_class.objects.count(),
            })
        
        # Group by app
        apps = {}
        for model_info in models_list:
            app = model_info['app_label']
            if app not in apps:
                apps[app] = []
            apps[app].append(model_info)
        
        context['apps'] = apps
        context['models_list'] = models_list
        
        # Build navbar config for navigation
        from ..configs import NavBarConfig, HyperlinkConfig
        
        nav_children = {
            'index': HyperlinkConfig(text="Home", link=reverse('bfe:index')),
        }
        for model_info in models_list:
            nav_children[model_info['model_name']] = HyperlinkConfig(
                text=model_info['name_plural'],
                link=model_info['list_url'],
            )
        
        navbar_cfg = NavBarConfig(
            name="bfe_nav",
            text="BFE Model Views",
            title_button=True,
            children=nav_children,
        )
        
        from ..widgets import NavBarWidget
        navbar = NavBarWidget(config=navbar_cfg)
        context['navbar'] = navbar
        context = self._add_media_to_context(context, navbar)
        
        return context
    
    def _add_media_to_context(self, context: dict, *widgets) -> dict:
        css_links, js_scripts = aggregate_media(*widgets)
        context['all_css'] = css_links
        context['all_js'] = js_scripts
        return context


class BFEViewMixin:
    """
    Mixin that adds BFE widget rendering to Django views.
    
    Provides the model_view attribute and integrates BFE's
    media aggregation with the template context.
    """
    model_view: BFEModelView = None
    template_name_suffix: str = ""
    
    def get_template_names(self):
        """
        Return template names to try, in order:
        1. Custom template if specified
        2. App-specific template: {app_label}/{model_name}{suffix}.html
        3. BFE default template: byefrontend/model_views/{suffix_name}.html
        """
        if self.template_name:
            return [self.template_name]
        
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        
        # Convert _list -> list, _detail -> detail, etc.
        suffix_name = self.template_name_suffix.lstrip('_')
        
        return [
            f"{app_label}/{model_name}{self.template_name_suffix}.html",
            f"byefrontend/model_views/{suffix_name}.html",
        ]
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Add model metadata
        context['model_name'] = self.model._meta.verbose_name.title()
        context['model_name_plural'] = self.model._meta.verbose_name_plural.title()
        context['app_label'] = self.model._meta.app_label
        
        # Add URL names for navigation
        name_prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        context['list_url_name'] = f"bfe:{name_prefix}_list"
        context['create_url_name'] = f"bfe:{name_prefix}_create"
        context['detail_url_name'] = f"bfe:{name_prefix}_detail"
        context['update_url_name'] = f"bfe:{name_prefix}_update"
        context['delete_url_name'] = f"bfe:{name_prefix}_delete"
        
        # Add navbar for navigation between models
        context['navbar'] = self._build_navbar()
        
        return context
    
    def _build_navbar(self):
        """Build a NavBarWidget with links to all registered models."""
        from .registry import bfe
        from ..configs import NavBarConfig, HyperlinkConfig
        from ..widgets import NavBarWidget
        
        nav_children = {
            'index': HyperlinkConfig(text="Home", link=reverse('bfe:index')),
        }
        
        for model_class in bfe._registry:
            app_label = model_class._meta.app_label
            model_name = model_class._meta.model_name
            name_prefix = f"{app_label}_{model_name}"
            
            nav_children[model_name] = HyperlinkConfig(
                text=model_class._meta.verbose_name_plural.title(),
                link=reverse(f'bfe:{name_prefix}_list'),
            )
        
        navbar_cfg = NavBarConfig(
            name="bfe_nav",
            text="BFE",
            title_button=True,
            children=nav_children,
        )
        
        return NavBarWidget(config=navbar_cfg)
    
    def add_media_to_context(self, context: dict, *widgets) -> dict:
        """Add aggregated CSS/JS from widgets to context."""
        # Include navbar in media aggregation
        all_widgets = list(widgets)
        if 'navbar' in context:
            all_widgets.append(context['navbar'])
        
        css_links, js_scripts = aggregate_media(*all_widgets)
        context['all_css'] = css_links
        context['all_js'] = js_scripts
        return context


class BFEModelListView(BFEViewMixin, ListView):
    """
    Auto-generated list view using BFE widgets.
    
    Renders the queryset using the model_view's get_list_widget().
    """
    template_name_suffix = "_list"
    context_object_name = "object_list"
    
    def get_queryset(self):
        if self.model_view:
            return self.model_view.get_queryset(self.request)
        return super().get_queryset()
    
    def get_paginate_by(self, queryset):
        if self.model_view:
            return self.model_view.list_per_page
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.model_view:
            widget = self.model_view.get_list_widget(
                self.object_list,
                self.request,
            )
            context['bfe_widget'] = widget
            context = self.add_media_to_context(context, widget)
        
        return context


class BFEModelDetailView(BFEViewMixin, DetailView):
    """
    Auto-generated detail view using BFE widgets.
    
    Renders a single object using the model_view's get_detail_widget().
    """
    template_name_suffix = "_detail"
    context_object_name = "object"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.model_view:
            widget = self.model_view.get_detail_widget(
                self.object,
                self.request,
            )
            context['bfe_widget'] = widget
            context = self.add_media_to_context(context, widget)
        
        # Add edit/delete URLs for this object
        name_prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        context['edit_url'] = reverse(f"bfe:{name_prefix}_update", args=[self.object.pk])
        context['delete_url'] = reverse(f"bfe:{name_prefix}_delete", args=[self.object.pk])
        
        return context


class BFEModelCreateView(BFEViewMixin, CreateView):
    """
    Auto-generated create view using BFE form widgets.
    
    Uses model_view's get_form_widget() for rendering.
    """
    template_name_suffix = "_form"
    
    def get_form_class(self):
        """We don't use Django's form system - return None."""
        return None
    
    def get_form(self, form_class=None):
        """Return BFE form widget instead of Django form."""
        if self.model_view:
            return self.model_view.get_form_widget(
                self.request,
                instance=None,
            )
        return None
    
    def get_context_data(self, **kwargs):
        # Don't call parent - we handle form differently
        context = BFEViewMixin.get_context_data(self, **kwargs)
        
        if self.model_view:
            widget = self.model_view.get_form_widget(
                self.request,
                instance=None,
            )
            context['bfe_widget'] = widget
            context['bfe_form'] = widget
            context['form_title'] = f"Create {self.model._meta.verbose_name.title()}"
            context = self.add_media_to_context(context, widget)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        self.object = None
        
        if self.model_view:
            form_widget = self.model_view.get_form_widget(request, instance=None)
            
            if form_widget.is_valid():
                # Create the object from cleaned data
                cleaned = form_widget.cleaned_data
                self.object = self.model.objects.create(**cleaned)
                return self.form_valid_redirect()
            
            # Re-render with errors
            context = self.get_context_data()
            context['bfe_widget'] = form_widget
            context['bfe_form'] = form_widget
            context = self.add_media_to_context(context, form_widget)
            return self.render_to_response(context)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid_redirect(self):
        """Redirect after successful creation."""
        name_prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        url = reverse(f"bfe:{name_prefix}_detail", args=[self.object.pk])
        return HttpResponseRedirect(url)


class BFEModelUpdateView(BFEViewMixin, UpdateView):
    """
    Auto-generated update view using BFE form widgets.
    
    Uses model_view's get_form_widget() for rendering.
    """
    template_name_suffix = "_form"
    
    def get_form_class(self):
        """We don't use Django's form system - return None."""
        return None
    
    def get_form(self, form_class=None):
        """Return BFE form widget instead of Django form."""
        if self.model_view:
            return self.model_view.get_form_widget(
                self.request,
                instance=self.object,
            )
        return None
    
    def get_context_data(self, **kwargs):
        # Don't call parent - we handle form differently
        context = BFEViewMixin.get_context_data(self, **kwargs)
        context['object'] = self.object
        
        if self.model_view:
            widget = self.model_view.get_form_widget(
                self.request,
                instance=self.object,
            )
            context['bfe_widget'] = widget
            context['bfe_form'] = widget
            context['form_title'] = f"Edit {self.model._meta.verbose_name.title()}"
            context = self.add_media_to_context(context, widget)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        self.object = self.get_object()
        
        if self.model_view:
            form_widget = self.model_view.get_form_widget(request, instance=self.object)
            
            if form_widget.is_valid():
                # Update the object from cleaned data
                cleaned = form_widget.cleaned_data
                for key, value in cleaned.items():
                    setattr(self.object, key, value)
                self.object.save()
                return self.form_valid_redirect()
            
            # Re-render with errors
            context = self.get_context_data()
            context['bfe_widget'] = form_widget
            context['bfe_form'] = form_widget
            context = self.add_media_to_context(context, form_widget)
            return self.render_to_response(context)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid_redirect(self):
        """Redirect after successful update."""
        name_prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        url = reverse(f"bfe:{name_prefix}_detail", args=[self.object.pk])
        return HttpResponseRedirect(url)


class BFEModelDeleteView(BFEViewMixin, DeleteView):
    """
    Auto-generated delete confirmation view.
    
    Shows a confirmation page before deleting.
    """
    template_name_suffix = "_confirm_delete"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Delete {self.model._meta.verbose_name.title()}"
        return context
    
    def get_success_url(self):
        name_prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        return reverse(f"bfe:{name_prefix}_list")

