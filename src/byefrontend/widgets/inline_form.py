# src/byefrontend/widgets/inline_form.py
from __future__ import annotations
from typing import Any

from .form import BFEFormWidget          # full Django-Form logic lives here
from ..configs.inline_form import InlineFormConfig
from ..builders import ChildBuilderRegistry


class InlineFormWidget(BFEFormWidget):
    """A drop-in replacement that lays the form out in a *flex* row."""
    DEFAULT_CONFIG = InlineFormConfig()
    aria_label     = "Inline form"

    cfg = property(lambda self: self.config)

    # ------------------------------------------------------------------ #
    #  Rendering – call the parent, then patch the <form …> tag
    # ------------------------------------------------------------------ #
    def _render(self, name: str | None = None, value: Any = None,
                attrs=None, renderer=None, **kwargs) -> str:

        html = super()._render(name=name, value=value,
                                attrs=attrs, renderer=renderer, **kwargs)

        # first occurrence of  class="bfe-form-widget"
        gap   = f"{self.cfg.gap}rem"
        wrap  = "wrap" if self.cfg.wrap else "nowrap"
        patch = (f'class="bfe-form-widget bfe-inline-form" '
                 f'style="display:flex;flex-wrap:{wrap};gap:{gap};"')

        return html.replace('class="bfe-form-widget"', patch, 1)

    # no extra assets – everything re-uses existing CSS/JS
    class Media:
        css = {}
        js  = ()


# --- builder hook so configs → widgets resolution keeps working -------- #
@ChildBuilderRegistry.register(InlineFormConfig)
def _build_inline_form(cfg: InlineFormConfig, parent):
    return InlineFormWidget(config=cfg, parent=parent)
