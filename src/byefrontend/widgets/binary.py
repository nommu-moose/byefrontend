from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget, BFEBaseFormWidget
from ..builders import ChildBuilderRegistry
from ..configs.binary import CheckBoxConfig, RadioConfig


class CheckBoxWidget(BFEBaseFormWidget):
    DEFAULT_CONFIG = CheckBoxConfig()

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        checked = " checked" if cfg.checked else ""
        html = (
            f'<input type="checkbox" id="{self.id}" name="{name}"{checked}>'
            f'<label for="{self.id}">{cfg.label or name}</label>'
        )
        return mark_safe(html)


class RadioWidget(BFEBaseWidget, Widget):
    DEFAULT_CONFIG = RadioConfig()

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        checked = " checked" if cfg.checked else ""
        html = (
            f'<input type="radio" id="{self.id}" '
            f'name="{cfg.group_name}" value="{cfg.value}"{checked}>'
            f'<label for="{self.id}">{cfg.label or cfg.value}</label>'
        )
        return mark_safe(html)


@ChildBuilderRegistry.register(CheckBoxConfig)
def _build_checkbox(cfg: CheckBoxConfig, parent):
    return CheckBoxWidget(config=cfg, parent=parent)


@ChildBuilderRegistry.register(RadioConfig)
def _build_radio(cfg: RadioConfig, parent):
    return RadioWidget(config=cfg, parent=parent)
