# src/byefrontend/widgets/title.py
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.title import TitleConfig

class TitleWidget(BFEBaseWidget):
    DEFAULT_CONFIG = TitleConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        tag = f"h{min(max(cfg.level,1),6)}"
        return mark_safe(f"<{tag} id='{self.id}' class='bfe-title'>{cfg.text}</{tag}>")
