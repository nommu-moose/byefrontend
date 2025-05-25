from __future__ import annotations
import json
import uuid
from django.utils.safestring import mark_safe
from ..configs import NavBarConfig, HyperlinkConfig
from .base import BFEBaseWidget
from .hyperlink import HyperlinkWidget
from ..builders import build_children, ChildBuilderRegistry


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

    def __init__(self,
                 config: NavBarConfig | None = None,
                 *,
                 parent: "NavBarWidget | None" = None,
                 **overrides):
        """
        Parameters

        config:
            A frozen :class:`NavBarConfig`.  When *None*, the defaults from
            `DEFAULT_CONFIG` are used.
        parent:
            Internal pointer used when nesting navbars.
        overrides:
            Optional *legacy* keyword tweaks that are merged into a copy of
            *config* via :pyfunc:`dataclasses.replace`.  Keep them around so
            existing call-sites do not break while you migrate.
        """
        super().__init__(config=config, parent=parent, **overrides)

        # children derived once and wrapped in MappingProxyType
        self._children = build_children(self, self.cfg.children)

    # properties delegated to config (read-only)
    # keeping as attributes preserves templates that access them and helps cache
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
    def selected_id(self):
        return self.cfg.selected_id

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        """
        Generates a very small HTML shell; the heavy lifting is done by
        `navbar.js`, fed via a JSON blob emitted here.
        """
        payload = self.to_json()
        payload["selected_id"] = self.cfg.selected_id
        data_json = json.dumps(payload)
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

    def _own_json(self):
        return {
            "uid": uuid.uuid4().hex,
            "name": self.cfg.name,
            "text": self.cfg.text,
            "title_button": self.cfg.title_button,
            "link": self.cfg.link,
            # "selected": self._is_selected(),   # from legacy, not implemented again yet
        }

    class Media:
        css = {"all": ("byefrontend/css/navbar.css",)}
        js = ("byefrontend/js/navbar.js",)


@ChildBuilderRegistry.register(NavBarConfig)
def _build_navbar(cfg: NavBarConfig, parent):
    return NavBarWidget(config=cfg, parent=parent)
