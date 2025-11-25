"""
SectionWidget - Titled, optionally collapsible section container.
"""
from __future__ import annotations

import html
from typing import Any

from django.utils.safestring import mark_safe

from ..builders import build_children, ChildBuilderRegistry
from ..configs.section import SectionConfig
from .base import BFEBaseWidget


class SectionWidget(BFEBaseWidget):
    """
    A titled section that can contain child widgets.
    
    Supports optional collapsible behavior with CSS-only
    animation using <details>/<summary> elements.
    """
    DEFAULT_CONFIG = SectionConfig()
    aria_label = "Section container"
    
    def __init__(
        self,
        config: SectionConfig | None = None,
        *,
        parent: BFEBaseWidget | None = None,
        **overrides,
    ):
        super().__init__(config=config, parent=parent, **overrides)
        self._children = build_children(self, self.cfg.children)
    
    cfg = property(lambda self: self.config)
    
    @property
    def children(self):
        return self._children
    
    def _render(
        self,
        name: str | None = None,
        value: Any = None,
        attrs=None,
        renderer=None,
        **kwargs,
    ) -> str:
        cfg = self.cfg
        
        # Build CSS classes
        classes = ["bfe-section"]
        if cfg.bordered:
            classes.append("bfe-section--bordered")
        if cfg.padded:
            classes.append("bfe-section--padded")
        if cfg.collapsible:
            classes.append("bfe-section--collapsible")
        
        class_str = " ".join(classes)
        
        # Render children
        inner = "".join(
            child.render(name=child_name, value=value, renderer=renderer)
            for child_name, child in self.children.items()
        )
        
        # Build heading
        heading = ""
        if cfg.title:
            tag = f"h{min(max(cfg.level, 1), 6)}"
            escaped_title = html.escape(cfg.title)
            heading = f"<{tag} class='bfe-section-title'>{escaped_title}</{tag}>"
        
        # Collapsible uses <details>/<summary>
        if cfg.collapsible:
            open_attr = "" if cfg.collapsed else " open"
            return mark_safe(
                f"<details id='{self.id}' class='{class_str}'{open_attr}>"
                f"<summary class='bfe-section-summary'>{html.escape(cfg.title)}</summary>"
                f"<div class='bfe-section-content'>{inner}</div>"
                f"</details>"
            )
        
        # Non-collapsible section
        return mark_safe(
            f"<section id='{self.id}' class='{class_str}'>"
            f"{heading}"
            f"<div class='bfe-section-content'>{inner}</div>"
            f"</section>"
        )
    
    class Media:
        css = {"all": ("byefrontend/css/section.css",)}
        js = ()


@ChildBuilderRegistry.register(SectionConfig)
def _build_section(cfg: SectionConfig, parent):
    return SectionWidget(config=cfg, parent=parent)

