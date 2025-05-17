from __future__ import annotations
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.paragraph import ParagraphConfig
from ..builders import ChildBuilderRegistry


class ParagraphWidget(BFEBaseWidget):
    """Simple wrapper around a themed <p> element."""
    DEFAULT_CONFIG = ParagraphConfig()
    aria_label     = "Paragraph text"

    # handy shorthand
    cfg = property(lambda self: self.config)

    # ── rendering ─────────────────────────────────────────────
    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg       = self.cfg
        classes   = ["bfe-paragraph", *cfg.classes]
        if cfg.italic:
            classes.append("bfe-paragraph--italic")

        class_attr  = " ".join(classes)
        style_attr  = f'text-align:{cfg.align};' if cfg.align else ""

        return mark_safe(
            f'<p id="{self.id}" class="{class_attr}" style="{style_attr}">{cfg.text}</p>'
        )

    # tiny optional stylesheet
    class Media:
        css = {"all": ("byefrontend/css/paragraph.css",)}
        js  = ()


@ChildBuilderRegistry.register(ParagraphConfig)
def _build_paragraph(cfg: ParagraphConfig, parent):
    return ParagraphWidget(config=cfg, parent=parent)
