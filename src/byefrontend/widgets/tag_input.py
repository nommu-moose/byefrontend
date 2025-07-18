from __future__ import annotations

import html, json
from typing import Any, Sequence

from django.utils.safestring import mark_safe

from .base import BFEFormCompatibleWidget
from .label import LabelWidget
from ..builders import ChildBuilderRegistry
from ..configs.label import LabelConfig
from ..configs.tag_input import TagInputConfig


class TagInputWidget(BFEFormCompatibleWidget):
    """Text field that turns comma-separated entries into removable tags."""

    DEFAULT_CONFIG = TagInputConfig()
    aria_label = "Tags input"

    cfg = property(lambda self: self.config)

    def _render(self, name: str | None = None, value: Any = None,
                attrs=None, renderer=None, **kwargs) -> str:
        cfg = self.cfg
        placeholder = cfg.placeholder or self.attrs.get("placeholder", "")
        base_id = self.id
        hid = f"{base_id}_hidden"
        input_id = f"{base_id}_input"
        suggest_id = f"{base_id}_suggest"

        initial: list[str] = []
        val = value if value is not None else self.attrs.get("value")
        if isinstance(val, str):
            initial = [t.strip() for t in val.split(',') if t.strip()]
        elif isinstance(val, Sequence):
            initial = [str(t).strip() for t in val if str(t).strip()]

        tags_html = "".join(
            f'<span class="bfe-tag" data-tag="{html.escape(t)}">{html.escape(t)}'
            f'<button type="button" class="bfe-tag-remove">\u00d7</button></span>'
            for t in initial
        )

        input_html = (
            f'<input type="text" id="{input_id}" class="bfe-tag-input-field"'
            f'{f" placeholder=\"{html.escape(placeholder)}\"" if placeholder else ""}>'
        )
        hidden_html = (
            f'<input type="hidden" id="{hid}" name="{name or base_id}"'
            f' value="{html.escape(",".join(initial))}">'
        )
        suggest_html = f'<div id="{suggest_id}" class="bfe-tag-suggestions"></div>'

        wrapper = (
            f'<div id="{base_id}" class="bfe-tag-input-wrapper"'
            f' data-suggestions="{html.escape(json.dumps(list(cfg.suggestions)))}">'
            f'{hidden_html}{tags_html}{input_html}{suggest_html}</div>'
        )

        if cfg.is_in_form:
            label_html = ""
        else:
            lbl_cfg = LabelConfig(text=cfg.label or name, html_for=input_id)
            label_html = LabelWidget(config=lbl_cfg, parent=self).render()

        return mark_safe(
            f'<div class="text-input-wrapper">{label_html}{wrapper}</div>'
        )

    class Media:
        css = {"all": ("byefrontend/css/tag_input.css",)}
        js = ("byefrontend/js/tag_input.js",)


@ChildBuilderRegistry.register(TagInputConfig)
def _build_taginput(cfg: TagInputConfig, parent):
    return TagInputWidget(config=cfg, parent=parent)
