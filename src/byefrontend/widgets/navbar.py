# ── inside src/byefrontend/widgets/containers.py ────────────────────────────────
from __future__ import annotations

import json
import uuid
from typing import Mapping

from django.utils.safestring import mark_safe

from ..configs import NavBarConfig, HyperlinkConfig
from .base import BFEBaseWidget
from .hyperlink import HyperlinkWidget


class NavBarWidget(BFEBaseWidget):
    """
    Hierarchical navigation bar driven entirely by an immutable
    :class:`NavBarConfig`.

    The widget keeps read-only references to its child widgets, so any change
    requires *replacing* the whole config object (and therefore the widget) –
    perfect for deterministic caching later on.
    """

    DEFAULT_CONFIG = NavBarConfig()
    aria_label = "Navbar for the site."
    DEFAULT_NAME = "navbar_widget"

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self,
                 config: NavBarConfig | None = None,
                 *,
                 parent: "NavBarWidget | None" = None,
                 **overrides):
        """
        Parameters
        ----------
        config:
            A frozen :class:`NavBarConfig`.  When *None*, the defaults from
            ``DEFAULT_CONFIG`` are used.
        parent:
            Internal pointer used when nesting navbars.
        overrides:
            Optional *legacy* keyword tweaks that are merged into a copy of
            *config* via :pyfunc:`dataclasses.replace`.  Keep them around so
            existing call-sites do not break while you migrate.
        """
        super().__init__(config=config, parent=parent, **overrides)

        # cached_render / cached_media bookkeeping already handled by base class
        self.children: Mapping[str, NavBarWidget | HyperlinkWidget] = {}
        self._initialise_children()

    # ── properties delegated to config (read-only)─────────────────────────────
    # Keeping these as attributes preserves templates that access them
    cfg = property(lambda self: self.config)

    @property
    def text(self) -> str:
        return self.cfg.text

    @property
    def title_button(self) -> bool:
        return self.cfg.title_button

    @property
    def link(self) -> str | None:
        return self.cfg.link

    @property
    def selected_path(self):
        return self.cfg.selected_path

    # ── private helpers ───────────────────────────────────────────────────────

    def _initialise_children(self) -> None:
        """
        Turn the *config*’s mapping into real widget instances.
        Supports mixed depth (NavBarConfig / HyperlinkConfig).
        """
        for key, child_cfg in self.cfg.children.items():
            if isinstance(child_cfg, NavBarConfig):
                self.children[key] = NavBarWidget(config=child_cfg, parent=self)
            elif isinstance(child_cfg, HyperlinkConfig):
                self.children[key] = HyperlinkWidget(config=child_cfg, parent=self)
            else:   # safety net for stray dicts during transition
                raise TypeError(
                    f"Unsupported child config type {type(child_cfg)!r} "
                    "– convert it to NavBarConfig or HyperlinkConfig first."
                )

    # ── rendering & media -----------------------------------------------------

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        """
        Generates a very small HTML shell; the heavy lifting is done by
        `navbar.js`, fed via a JSON blob emitted here.
        """
        data_json = json.dumps(self._create_data_json(
            selected_path=list(self.cfg.selected_path)
        ))
        return mark_safe(
            f"""
            <div class="navbar-wrapper">
              <nav class="navbar-container"
                   aria-label="{self.aria_label}"
                   data-nav-config='{data_json}'>
              </nav>
            </div>
            """
        )

    def _create_data_json(self, *, selected_path: list[str], first=True):
        """
        Recursively turn the *widget* tree into a JSON-serialisable structure
        understood by the JavaScript driver.

        The algorithm mirrors the original behaviour but now trusts the
        immutable config instead of ad-hoc attributes.
        """
        is_selected_here = first or (selected_path and self.cfg.name == selected_path[0])
        child_path = selected_path[1:] if is_selected_here else []

        children_serialised = []
        for key, child_widget in self.children.items():
            if isinstance(child_widget, NavBarWidget):
                children_serialised.append(
                    child_widget._create_data_json(selected_path=child_path, first=False)
                )
            else:   # HyperlinkWidget
                child_selected = bool(child_path) and key == child_path[0]
                children_serialised.append({
                    "uid": str(uuid.uuid4()),
                    "text": child_widget.text,
                    "link": child_widget.link,
                    "selected": child_selected,
                })

        return {
            "uid": str(uuid.uuid4()),
            "name": self.cfg.name,
            "text": self.cfg.text,
            "title_button": self.cfg.title_button,
            "link": self.cfg.link,
            "selected": is_selected_here,
            "children": children_serialised,
        }

    # ── static media declaration ---------------------------------------------

    class Media:
        css = {"all": ("byefrontend/css/navbar.css",)}
        js = ("byefrontend/js/navbar.js",)
