# ── src/byefrontend/widgets/text_editor.py ────────────────────────────
"""
Rich-text editor widget.

Changes vs. the original version
• Inherits from BFEFormCompatibleWidget so Django treats it as a form field.
• Adds a hidden <input> that always holds the editor’s HTML -> POST data works.
• Small JS additions (in text_editor.js) keep that hidden input in sync.
"""

from __future__ import annotations

import html
from typing import Any

from django.utils.safestring import mark_safe

from ..configs.text_editor import TextEditorConfig
from ..widgets.base import BFEFormCompatibleWidget
from ..builders import ChildBuilderRegistry


class TextEditorWidget(BFEFormCompatibleWidget):
    DEFAULT_CONFIG = TextEditorConfig()
    aria_label     = "Rich text editor"

    cfg = property(lambda self: self.config)

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self,
                name: str | None = None,
                value: Any = None,
                attrs=None,
                renderer=None,
                **kwargs):
        cfg  = self.cfg

        # ----------------------------------------------------------------
        #  1. Pick the “initial” HTML in this preference order:
        #     a) explicit *value* passed in from Django’s <form> plumbing
        #     b) cfg.value  (new field you just added)
        #     c) attrs["value"]  (fallback, mirrors CharInputWidget)
        # ----------------------------------------------------------------
        initial_html: str = (
            (value if value is not None else None)
            or (cfg.value if cfg.value is not None else None)
            or self.attrs.get("value")
            or ""
        ).strip()

        # editor + hidden-input need unique, stable IDs
        eid   = self.id
        tid   = f"{eid}_toolbar"
        edid  = f"{eid}_editor"
        hid   = f"{eid}_hidden"

        # ----------------------------------------------------------------
        #  2. Placeholder: only add the data-attribute when *no* content
        # ----------------------------------------------------------------
        placeholder_attr = (
            f' data-placeholder="{html.escape(cfg.placeholder)}"'
            if cfg.placeholder and not initial_html
            else ""
        )

        # ---------- full toolbar ----------
        toolbar = f"""
        <div id="{tid}" class="bfe-text-editor-toolbar" role="toolbar">
          <button type=button data-cmd="bold"><b>B</b></button>
          <button type=button data-cmd="italic"><i>I</i></button>
          <button type=button data-cmd="underline"><u>U</u></button>
          <button type=button data-cmd="strikeThrough"><s>S</s></button>

          <label>Color <input type="color" data-fore></label>
          <label>Highlight <input type="color" data-back></label>

          <button type=button data-cmd="insertUnorderedList">• List</button>
          <button type=button data-cmd="insertOrderedList">1. List</button>

          <button type=button data-cmd="justifyLeft">Left</button>
          <button type=button data-cmd="justifyCenter">Center</button>
          <button type=button data-cmd="justifyRight">Right</button>

          <select data-block>
            <option value="">Heading…</option>
            <option value="H1">H1</option><option value="H2">H2</option>
            <option value="H3">H3</option><option value="H4">H4</option>
            <option value="H5">H5</option><option value="H6">H6</option>
            <option value="P">Paragraph</option>
          </select>

          <button type=button data-special="checkbox">Checkbox</button>
          <button type=button data-special="table">Table</button>
          <button type=button data-special="deleteTable">Delete Table</button>
          <button type=button data-special="image">Image</button>
        </div>
        """

        editor_div = (
            f'<div id="{edid}" class="bfe-text-editor-area" contenteditable="true"'
            f'{placeholder_attr} '
            f'style="min-height:{cfg.min_height_rem}rem;">'
            f'{initial_html}</div>'
        )

        # 5. hidden field keeps the HTML for Django -> escape for attribute ctx
        hidden_input = (
            f'<input type="hidden" id="{hid}" name="{name or eid}" '
            f'value="{html.escape(initial_html)}">'
        )

        return mark_safe(
            f'<div id="{eid}" class="bfe-text-editor-wrapper" '
            f'data-compact="{str(cfg.toolbar_compact).lower()}">'
            f'{toolbar}{editor_div}{hidden_input}</div>'
        )

    # ------------------------------------------------------------------ #
    #  Static assets
    # ------------------------------------------------------------------ #
    class Media:
        css = {"all": ("byefrontend/css/text_editor.css",)}
        js = ("byefrontend/js/text_editor.js",)


@ChildBuilderRegistry.register(TextEditorConfig)
def _build(cfg: TextEditorConfig, parent):
    return TextEditorWidget(config=cfg, parent=parent)
