# NEW FILE – the widget that renders the whole group
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs.radio_group import RadioGroupConfig

class RadioGroupWidget(BFEBaseWidget, Widget):
    DEFAULT_CONFIG = RadioGroupConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        current   = value if value is not None else cfg.selected
        separator = " " if cfg.layout == "inline" else "<br>"

        pieces = []
        for val, label in cfg.choices:
            checked = " checked" if (current == val) else ""
            html = (
                f'<label>'
                f'<input type="radio" name="{cfg.name}" value="{val}"{checked}>'
                f'{label}'
                f'</label>'
            )
            pieces.append(html)

        return mark_safe(separator.join(pieces))

    class Media:
        css = {}
        js  = ()


@ChildBuilderRegistry.register(RadioGroupConfig)
def _build_radio_group(cfg: RadioGroupConfig, parent):
    return RadioGroupWidget(config=cfg, parent=parent)
