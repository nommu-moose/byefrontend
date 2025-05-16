from __future__ import annotations

from typing import Any

from django.utils.safestring import mark_safe

from ..configs.inline_group import InlineGroupConfig
from ..builders import build_children, ChildBuilderRegistry
from .base import BFEBaseWidget

class InlineGroupWidget(BFEBaseWidget):
    """
    Simple flexbox container.  It just lines up its immutable `children`
    and hands back their `.render()` output – nothing more.
    """

    DEFAULT_CONFIG = InlineGroupConfig()
    aria_label = "Inline group"

    # ── construction ───────────────────────────────────────────────
    def __init__(self,
                 config: InlineGroupConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        super().__init__(config=config, parent=parent, **overrides)
        self._children = build_children(self, self.cfg.children)

    cfg = property(lambda self: self.config)

    # ── rendering ──────────────────────────────────────────────────
    def _render(self, name: str | None = None, value: Any = None,
                attrs=None, renderer=None, **kwargs) -> str:
        gap = f"{self.cfg.gap}rem"
        wrap_value = "wrap" if self.cfg.wrap else "nowrap"

        # • merge the mandatory base class with any caller-supplied classes
        classes = " ".join(["bfe-inline-group", *self.cfg.classes])

        # • emit inline style so gap / wrapping take effect without extra CSS
        style = f"gap:{gap};flex-wrap:{wrap_value};"

        inner = "".join(child.render(name=name, value=value, renderer=renderer)
                        for child in self.children.values())

        return mark_safe(
            f'<div id="{self.id}" class="{classes}" style="{style}">{inner}</div>'
        )

    # ── static media  (tiny, CSS-only) ─────────────────────────────
    class Media:
        css = {"all": ("byefrontend/css/inline_group.css",)}
        js  = ()

# Register with the builders registry so InlineGroupConfig becomes
# composable inside any other widget.
@ChildBuilderRegistry.register(InlineGroupConfig)
def _build_inline(cfg: InlineGroupConfig, parent):
    from byefrontend.widgets.inline_group import InlineGroupWidget
    return InlineGroupWidget(config=cfg, parent=parent)
