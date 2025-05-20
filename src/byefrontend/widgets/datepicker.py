# ── src/byefrontend/widgets/datepicker.py ─────────────────────────
from __future__ import annotations
from django.utils.safestring import mark_safe
from .base import BFEFormCompatibleWidget
from .label import LabelWidget
from ..builders import ChildBuilderRegistry
from ..configs.label import LabelConfig
from ..configs.datepicker import DatePickerConfig


class DatePickerWidget(BFEFormCompatibleWidget):
    """
    Lightweight <input type="date"> wrapper that inherits the
    look-and-feel of CharInputWidget.
    """
    DEFAULT_CONFIG = DatePickerConfig()
    aria_label = "Choose a date"

    # shorthand
    cfg = property(lambda self: self.config)

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.cfg
        base_id   = self.id
        placeholder = cfg.placeholder or self.attrs.get("placeholder", "")
        required  = " required" if cfg.required else ""
        readonly  = " readonly" if cfg.readonly else ""
        disabled  = " disabled" if cfg.disabled else ""
        min_attr  = f' min="{cfg.min_date}"' if cfg.min_date else ""
        max_attr  = f' max="{cfg.max_date}"' if cfg.max_date else ""

        # precedent for initial value: explicit > attrs["value"]
        val_attr = ""
        if value is not None:
            val_attr = f' value="{value}"'
        elif (dv := self.attrs.get("value")) is not None:
            val_attr = f' value="{dv}"'

        input_html = (
            f'<input type="date" id="{base_id}" name="{name}" '
            f'class="bfe-text-entry-field bfe-date-picker-field"'
            f'{min_attr}{max_attr}{required}{readonly}{disabled}{val_attr}'
            f'{f" placeholder=\"{placeholder}\"" if placeholder else ""}>'
        )

        if cfg.is_in_form:
            label_html = ""
        else:
            label_cfg  = LabelConfig(text=cfg.label or name, html_for=base_id)
            label_html = LabelWidget(config=label_cfg, parent=self).render()

        return mark_safe(
            f'<div class="text-input-wrapper">{label_html}{input_html}</div>'
        )

    class Media:       # styling re-uses .bfe-text-entry-field, so no extra CSS
        css = {}
        js  = ()


@ChildBuilderRegistry.register(DatePickerConfig)
def _build_datepicker(cfg: DatePickerConfig, parent):
    return DatePickerWidget(config=cfg, parent=parent)
