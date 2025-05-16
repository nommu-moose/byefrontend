from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs import LabelConfig


class LabelWidget(BFEBaseWidget):
    DEFAULT_CONFIG = LabelConfig()

    def __init__(self, config: LabelConfig | None = None, *, parent=None, **overrides):
        super().__init__(config=config, parent=parent, **overrides)

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config

        classes = ("bfe-label", *cfg.classes)
        class_attr = " ".join(classes)

        for_attr = f' for="{cfg.html_for}"' if cfg.html_for else ""
        return mark_safe(
            f'<{cfg.tag}{for_attr} id="{self.id}" '
            f'class="{class_attr}">{cfg.text}</{cfg.tag}>'
        )


@ChildBuilderRegistry.register(LabelConfig)
def _build_label(cfg: LabelConfig, parent):
    return LabelWidget(config=cfg, parent=parent)
