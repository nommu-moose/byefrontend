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

        eid  = self.id                     # wrapper div
        tid  = f"{eid}_toolbar"            # toolbar id
        edid = f"{eid}_editor"             # editable area id
        hid  = f"{eid}_hidden"             # hidden <input> id

        initial   = (value or "").strip()
        safe_init = html.escape(initial) or f"&lt;p&gt;{self.cfg.placeholder}&lt;/p&gt;"

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

        # ---------- editable area + hidden field ----------
        editor_div = (
            f'<div id="{edid}" class="bfe-text-editor-area" contenteditable="true" '
            f'style="min-height:{self.cfg.min_height_rem}rem;">{safe_init}</div>'
        )
        hidden_input = (
            f'<input type="hidden" id="{hid}" name="{name or eid}" '
            f'value="{html.escape(initial)}">'
        )

        return mark_safe(
            f'<div id="{eid}" class="bfe-text-editor-wrapper" '
            f'data-compact="{str(self.cfg.toolbar_compact).lower()}">'
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
