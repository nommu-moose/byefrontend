from __future__ import annotations
from typing import Any
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.button import ButtonConfig
from ..builders import ChildBuilderRegistry


class ButtonWidget(BFEBaseWidget):
    """Simple push-button widget that honours the global theme."""
    DEFAULT_CONFIG = ButtonConfig()
    aria_label = "Generic button"

    # shorthand todo: expand for api
    cfg = property(lambda self: self.config)

    def _render(self,
                name: str | None = None,
                value: Any = None,
                attrs=None,
                renderer=None,
                **kwargs) -> str:
        cfg = self.cfg
        disabled = " disabled" if cfg.disabled else ""
        class_str = " ".join(cfg.classes)

        return mark_safe(
            f'<button id="{self.id}" type="{cfg.button_type}" '
            f'class="{class_str}"{disabled}>{cfg.text}</button>'
        )

    # root palette already ships .bfe-btn
    class Media:
        css = {}
        js = ()


@ChildBuilderRegistry.register(ButtonConfig)
def _build_button(cfg: ButtonConfig, parent):
    return ButtonWidget(config=cfg, parent=parent)
