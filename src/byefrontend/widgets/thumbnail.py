# src/byefrontend/widgets/thumbnail.py
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.thumbnail import ThumbnailConfig

class TinyThumbnailWidget(BFEBaseWidget):
    DEFAULT_CONFIG = ThumbnailConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        html = (
            f'<img id="{self.id}" class="bfe-thumbnail {" ".join(cfg.classes)}" '
            f'src="{cfg.src}" alt="{cfg.alt}" '
            f'style="width:{cfg.size_px}px;height:{cfg.size_px}px;object-fit:cover;border-radius:4px;">'
        )
        return mark_safe(html)
