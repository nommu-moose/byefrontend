from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs.title import TitleConfig


class TitleWidget(BFEBaseWidget):
    DEFAULT_CONFIG = TitleConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        tag = f"h{min(max(cfg.level,1),6)}"
        attrs = " ".join(f'{k}="{v}"' for k, v in cfg.attrs.items())
        return mark_safe(f"<{tag} id='{self.id}' class='bfe-title' {attrs}>{cfg.text}</{tag}>")


@ChildBuilderRegistry.register(TitleConfig)
def _build_paragraph(cfg: TitleConfig, parent):
    return TitleWidget(config=cfg, parent=parent)
