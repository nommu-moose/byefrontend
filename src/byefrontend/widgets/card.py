"""
Simple wrapper that renders its children inside a <div class="bfe-card">.
If *title* is set, a heading is inserted above the children.
"""

from __future__ import annotations
from typing import Any

from django.utils.safestring import mark_safe

from ..builders import build_children, ChildBuilderRegistry
from ..configs.card import CardConfig
from .base import BFEBaseWidget

class CardWidget(BFEBaseWidget):
    DEFAULT_CONFIG = CardConfig()
    aria_label     = "Card container"

    # ── construction ───────────────────────────────────────────────
    def __init__(self,
                 config: CardConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        super().__init__(config=config, parent=parent, **overrides)
        self._children = build_children(self, self.cfg.children)

    cfg = property(lambda self: self.config)

    # ── rendering ──────────────────────────────────────────────────
    def _render(self, name: str | None = None, value: Any = None,
                attrs=None, renderer=None, **kwargs) -> str:
        heading = ""
        if self.cfg.title:
            tag = f"h{min(max(self.cfg.level, 1), 6)}"
            heading = f"<{tag} class='bfe-card-title'>{self.cfg.title}</{tag}>"

        inner = "".join(child.render(name=name, value=value, renderer=renderer)
                        for child in self.children.values())

        return mark_safe(
            f"<div id='{self.id}' class='bfe-card'>{heading}{inner}</div>"
        )

    # – the card re-uses the existing .bfe-card look, so no extra assets
    class Media:
        css = {}
        js  = {}

# Register with the global child-builder so CardConfig
# can be nested inside other configs.
@ChildBuilderRegistry.register(CardConfig)
def _build_card(cfg: CardConfig, parent):
    return CardWidget(config=cfg, parent=parent)
