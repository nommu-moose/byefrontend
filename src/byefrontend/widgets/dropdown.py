# ── src/byefrontend/widgets/dropdown.py ───────────────────────────
from __future__ import annotations
from django.utils.safestring import mark_safe
from .base import BFEFormCompatibleWidget
from .label import LabelWidget
from ..builders import ChildBuilderRegistry
from ..configs.label import LabelConfig
from ..configs.dropdown import DropdownConfig


class DropdownWidget(BFEFormCompatibleWidget):
    """
    Simple <select> widget that shares the root palette & rounded radius.
    """
    DEFAULT_CONFIG = DropdownConfig()
    aria_label = "Select an option"

    cfg = property(lambda self: self.config)

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.cfg
        base_id = self.id
        required = " required" if cfg.required else ""
        disabled = " disabled" if cfg.disabled else ""

        # --- options -------------------------------------------------
        opts = []
        if cfg.placeholder:
            ph_sel = " selected" if (cfg.selected is None and value is None) else ""
            opts.append(
                f'<option value="" disabled{ph_sel}>{cfg.placeholder}</option>'
            )

        current = value if value is not None else cfg.selected
        for val, label in cfg.choices:
            sel = " selected" if val == current else ""
            opts.append(f'<option value="{val}"{sel}>{label}</option>')

        select_html = (
            f'<select id="{base_id}" name="{name}" '
            f'class="bfe-dropdown-select" {required}{disabled}>'
            f'{"".join(opts)}</select>'
        )

        if cfg.is_in_form:
            label_html = ""
        else:
            label_cfg  = LabelConfig(text=cfg.label or name, html_for=base_id)
            label_html = LabelWidget(config=label_cfg, parent=self).render()

        return mark_safe(
            f'<div class="text-input-wrapper">{label_html}{select_html}</div>'
        )

    class Media:
        css = {"all": ("byefrontend/css/dropdown.css",)}
        js  = ()


@ChildBuilderRegistry.register(DropdownConfig)
def _build_dropdown(cfg: DropdownConfig, parent):
    return DropdownWidget(config=cfg, parent=parent)
