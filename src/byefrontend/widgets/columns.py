"""
ColumnsWidget - Multi-column layout using CSS Grid.
"""
from __future__ import annotations

from typing import Any

from django.utils.safestring import mark_safe

from ..builders import ChildBuilderRegistry
from ..configs.columns import ColumnsConfig
from .base import BFEBaseWidget


class ColumnsWidget(BFEBaseWidget):
    """
    Multi-column layout widget using CSS Grid.
    
    Renders each column config as a child widget in its own
    grid column. Supports configurable ratios and responsive
    stacking.
    """
    DEFAULT_CONFIG = ColumnsConfig()
    aria_label = "Column layout"
    
    def __init__(
        self,
        config: ColumnsConfig | None = None,
        *,
        parent: BFEBaseWidget | None = None,
        **overrides,
    ):
        super().__init__(config=config, parent=parent, **overrides)
        
        # Build child widgets from column configs
        self._column_widgets: list[BFEBaseWidget] = []
        for i, col_cfg in enumerate(self.cfg.columns):
            widget = ChildBuilderRegistry.build(col_cfg, parent=self)
            self._column_widgets.append(widget)
    
    cfg = property(lambda self: self.config)
    
    @property
    def children(self):
        # Return as mapping for media aggregation
        return {f"col_{i}": w for i, w in enumerate(self._column_widgets)}
    
    def _render(
        self,
        name: str | None = None,
        value: Any = None,
        attrs=None,
        renderer=None,
        **kwargs,
    ) -> str:
        cfg = self.cfg
        
        # Calculate grid template columns
        if cfg.ratios and len(cfg.ratios) >= len(cfg.columns):
            template = " ".join(f"{r}fr" for r in cfg.ratios[:len(cfg.columns)])
        else:
            # Default to equal widths
            template = " ".join("1fr" for _ in cfg.columns)
        
        # Build inline styles
        styles = [
            "display: grid",
            f"grid-template-columns: {template}",
            f"gap: {cfg.gap}rem",
            f"align-items: {cfg.align}",
        ]
        style_str = "; ".join(styles)
        
        # Responsive stacking via CSS custom property
        data_attrs = ""
        if cfg.stack_below > 0:
            data_attrs = f' data-stack-below="{cfg.stack_below}"'
        
        # Render each column
        columns_html = []
        for widget in self._column_widgets:
            col_html = widget.render(name=name, value=value, renderer=renderer)
            columns_html.append(f"<div class='bfe-column'>{col_html}</div>")
        
        inner = "".join(columns_html)
        
        return mark_safe(
            f"<div id='{self.id}' class='bfe-columns' style='{style_str}'{data_attrs}>"
            f"{inner}"
            f"</div>"
        )
    
    class Media:
        css = {"all": ("byefrontend/css/columns.css",)}
        js = ()


@ChildBuilderRegistry.register(ColumnsConfig)
def _build_columns(cfg: ColumnsConfig, parent):
    return ColumnsWidget(config=cfg, parent=parent)

