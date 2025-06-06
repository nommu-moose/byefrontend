from __future__ import annotations
import uuid
from types import MappingProxyType
from dataclasses import replace
from typing import Iterable, Set, Any
from django.conf import settings
from django.forms.widgets import Media, Widget as _DjangoWidget
from django.urls import reverse
from django.utils.safestring import mark_safe
from ..configs.base import WidgetConfig


class BFEBaseWidget:
    """
    Unified widget base-class with future centralised cache handling.

    - only implements `_render()` and (optionally) `Media`; never touches _needs_render_recache / cached_render / etc
    - If you turn the global flag  `settings.BFE_WIDGET_CACHE`  to True you’ll hit a `NotImplementedError`
    """
    DEFAULT_CONFIG: WidgetConfig = WidgetConfig()
    DEFAULT_NAME: str = "widget"
    aria_label: str | None = None # subclasses may override
    cache_relevant_attrs: Set[str] = {
        # *Any* mutation of these attrs invalidates the cached HTML.
        "name", "id", "classes", "attrs",
        "label", "help_text", "required", "children",
    }

    def __init__(self,
                 config: WidgetConfig | None = None,
                 *,
                 parent=None,
                 **overrides):

        if config is None:
            config = self.DEFAULT_CONFIG
        if overrides:
            config = replace(config, **overrides)
        self.config: WidgetConfig = config


        self.parent = parent
        self.name = config.name
        self.id = config.html_id or self._generate_id()
        self.label = config.label
        self.help_text = config.help_text
        self.required = config.required
        self.value = None

        self._attrs: dict = dict(config.attrs)  # local, mutable copy

        self._render_cache_valid = False
        self._cached_render: str = ""
        self._media_cache_valid = False
        self._cached_media: Media | None = None

        self._children = MappingProxyType({})

    @staticmethod
    def _generate_id() -> str:
        return uuid.uuid4().hex

    # attrs proxied so templates can still do widget.attrs["foo"] = …
    @property
    def attrs(self) -> dict:
        return self._attrs

    @attrs.setter
    def attrs(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError("attrs must be a dict, got %r" % type(value))
        self._attrs = value
        self._invalidate_render_cache()

    def __setattr__(self, name, value):
        """on *any* attribute mutation invalidate render cache automatically - legacy, todo: remove"""
        super().__setattr__(name, value)
        if name in self.cache_relevant_attrs:
            self._invalidate_render_cache()
    
    def __html__(self):  # doesn't work yet
        return mark_safe(self.render())

    def render(self, name: str = None, value: object | None = None, attrs=None, renderer=None, **kwargs):
        """
        Single source of truth for caching strategy.

        - If global cache flag is *off*  -> always compute fresh HTML.
        - If caller passes *attrs*       -> consider it unique, bypass cache.
        - Otherwise                      -> cached HTML when valid.
        """
        use_cache = bool(getattr(settings, "BFE_WIDGET_CACHE", False))

        if attrs or not use_cache:
            return self._render(name, value, attrs=attrs, renderer=renderer, **kwargs)

        if not self._render_cache_valid:
            self._cached_render = self._render(name, value, renderer=renderer, **kwargs)
            self._render_cache_valid = True

        return self._cached_render

    def _render(self, name, value, attrs=None, renderer=None, **kwargs) -> str:
        """
        subclasses implement this
        """
        raise NotImplementedError

    @property
    def media(self) -> Media:
        use_cache = bool(getattr(settings, "BFE_WIDGET_CACHE", False))

        if not use_cache:
            return self._compute_media()

        if not self._media_cache_valid:
            self._cached_media = self._compute_media()
            self._media_cache_valid = True

        return self._cached_media

    def _compute_media(self) -> Media:
        """
        walk *immutable* children tree and aggregate Media
        """
        if getattr(settings, "BFE_WIDGET_CACHE", False):
            raise NotImplementedError(
                "Widget-level caching is ON but no cache backend exists. "
                "Disable BFE_WIDGET_CACHE before deploying."
            )

        own_media = Media(css=self.Media.css, js=self.Media.js)
        child_media = [child.media for child in self.children.values()
                       if hasattr(child, "media")]
        for cm in child_media:
            own_media += cm
        return own_media

    def _invalidate_render_cache(self):
        self._render_cache_valid = False
        if self.parent is not None:
            self.parent._invalidate_render_cache()

    def _invalidate_media_cache(self):
        self._media_cache_valid = False
        if self.parent is not None:
            self.parent._invalidate_media_cache()

    @property
    def children(self):
        return self._children

    def to_json(self) -> dict[str, Any]:
        """
        return JSON-serialisable payload for *this* widget, **including**
        JSON versions of all children.

        concrete widgets override `_own_json()` for their *own* payload
        (text, link, id, whatever) and the base visitor handles recursion.
        """
        own = self._own_json()
        if self.children:
            own["children"] = [child.to_json() for child in self.children.values()]
        return own

    # sensible default so leaf widgets don’t *have* to override
    def _own_json(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.__class__.__name__}

    # default, empty Media for widgets that don't declare any
    class Media:
        css = {}
        js = ()


class BFEFormCompatibleWidget(BFEBaseWidget, _DjangoWidget):
    """
    drop-in replacement for widgets that need Django’s
    form plumbing (value parsing, `value_omitted_from_data`, etc.).
    nothing inside bfe changes – you just inherit from this one
    instead of manually mixing `django.forms.Widget` in every widget.

    Example
    class CheckBoxWidget(BFEFormCompatibleWidget):
        DEFAULT_CONFIG = CheckBoxConfig()
        …
    """

    def __init__(self,
                 config: WidgetConfig | None = None,
                 *,
                 parent=None,
                 **overrides):

        BFEBaseWidget.__init__(self,
                               config=config,
                               parent=parent,
                               **overrides)
        # after this django sets up its private machinery,  __init__ only takes optional attrs-dict
        # bfe cached copy in `self._attrs`
        _DjangoWidget.__init__(self)
