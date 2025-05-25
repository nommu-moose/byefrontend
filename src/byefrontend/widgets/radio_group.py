from django.utils.safestring import mark_safe
from .base import BFEBaseWidget, BFEFormCompatibleWidget
from ..builders import ChildBuilderRegistry
from ..configs.radio_group import RadioGroupConfig


class RadioGroupWidget(BFEFormCompatibleWidget):
    DEFAULT_CONFIG = RadioGroupConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        current = value if value is not None else cfg.selected
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

        group_html = separator.join(pieces)

        if cfg.title is not None:
            tag = f"h{min(max(cfg.level,1),6)}"
            heading = f"<{tag} class='bfe-card-title'>{cfg.title}</{tag}>"
            group_html = f"<div id='{self.id}' class='bfe-card'>{heading}{group_html}</div>"

        return mark_safe(group_html)

    class Media:
        css = {}
        js = ()


@ChildBuilderRegistry.register(RadioGroupConfig)
def _build_radio_group(cfg: RadioGroupConfig, parent):
    return RadioGroupWidget(config=cfg, parent=parent)
