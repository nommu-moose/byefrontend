from __future__ import annotations
from dataclasses import replace
from typing import Any
from django.utils.safestring import mark_safe

from ..configs.text_editor import TextEditorConfig
from ..widgets.base import BFEBaseWidget
from ..builders import ChildBuilderRegistry


class TextEditorWidget(BFEBaseWidget):
    DEFAULT_CONFIG = TextEditorConfig()
    aria_label     = "Rich text editor"

    cfg = property(lambda self: self.config)

    # ---------- HTML ----------
    def _render(self, name: str | None = None, value: Any = None,
                attrs=None, renderer=None, **kwargs):
        eid  = self.id
        tid  = f"{eid}_toolbar"
        edid = f"{eid}_editor"
        initial = (value or "").strip() or f"<p>{self.cfg.placeholder}</p>"

        toolbar = f"""
        <div id="{tid}" class="bfe-text-editor-toolbar" role="toolbar">
          <button data-cmd="bold"><b>B</b></button>
          <button data-cmd="italic"><i>I</i></button>
          <button data-cmd="underline"><u>U</u></button>
          <button data-cmd="strikeThrough"><s>S</s></button>

          <label>Color <input type="color" data-fore></label>
          <label>Highlight <input type="color" data-back></label>

          <button data-cmd="insertUnorderedList">• List</button>
          <button data-cmd="insertOrderedList">1. List</button>

          <button data-cmd="justifyLeft">Left</button>
          <button data-cmd="justifyCenter">Center</button>
          <button data-cmd="justifyRight">Right</button>

          <select data-block>
            <option value="">Heading…</option>
            <option value="H1">H1</option><option value="H2">H2</option>
            <option value="H3">H3</option><option value="H4">H4</option>
            <option value="H5">H5</option><option value="H6">H6</option>
            <option value="P">Paragraph</option>
          </select>

          <button data-special="checkbox">Checkbox</button>
          <button data-special="table">Table</button>
          <button data-special="deleteTable">Delete Table</button>
          <button data-special="image">Image</button>
        </div>
        """

        editor = (
            f'<div id="{edid}" class="bfe-text-editor-area" '
            f'contenteditable="true" style="min-height:{self.cfg.min_height_rem}rem;">'
            f'{initial}</div>'
        )

        return mark_safe(
            f'<div id="{eid}" class="bfe-text-editor-wrapper" '
            f'data-compact="{str(self.cfg.toolbar_compact).lower()}">'
            f'{toolbar}{editor}</div>'
        )

    # ---------- static assets ----------
    class Media:
        css = {"all": ("byefrontend/css/text_editor.css",)}
        js  = ("byefrontend/js/text_editor.js",)


@ChildBuilderRegistry.register(TextEditorConfig)
def _build(cfg: TextEditorConfig, parent):
    return TextEditorWidget(config=cfg, parent=parent)
