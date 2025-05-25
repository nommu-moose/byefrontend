from __future__ import annotations
import html
from typing import Any
from django.utils.safestring import mark_safe
from .base import BFEFormCompatibleWidget
from ..builders import ChildBuilderRegistry
from ..configs.code_box import CodeBoxConfig


class CodeBoxWidget(BFEFormCompatibleWidget):
    """
    rich, live-highlighting code editor with colour pickers
    preserves all visual styles defined in code_box.css
    """

    DEFAULT_CONFIG = CodeBoxConfig()

    def _render(
        self,
        name: str | None = None,
        value: Any = None,
        attrs=None,
        renderer=None,
        **kwargs,
    ) -> str:
        cfg = self.config

        wid = self.id  # wrapper div
        eid = f"{wid}_editor"  # <pre contenteditable>
        hid = f"{wid}_hidden"  # hidden <input> for forms
        pickers = [f"{wid}_colour{i}Picker" for i in range(6)]

        initial = value if value is not None else (cfg.value or "")
        initial_html = html.escape(initial)

        colour_labels = (
            "Other text", "$VAR", "\\optional:",
            "{brackets}", "inner {var}", "optional line"
        )
        picker_html = "\n".join(
            f'<label style="margin-right:1rem;">'
            f'Colour {i} ({colour_labels[i]}): '
            f'<input type="color" id="{pickers[i]}" '
            f'value="{self._default_colour(i)}">'
            f'</label>'
            for i in range(6)
        )

        html_output = f"""
        <div id="{wid}" class="code-box-wrapper">
          <div class="code-box-controls" style="margin-bottom:.5rem;">
            {picker_html}
          </div>

          <pre id="{eid}"
               class="code-box"
               contenteditable="true"
               spellcheck="false">{initial_html}</pre>

          <!-- hidden field so Django forms still receive the value -->
          <input type="hidden" id="{hid}" name="{name or wid}"
                 value="{html.escape(initial)}">

          <!-- per-instance bootstrap -->
          <script>
            window.BFE_CODE_BOX_INIT = window.BFE_CODE_BOX_INIT || [];
            window.BFE_CODE_BOX_INIT.push({{
              editorId: "{eid}",
              hiddenId: "{hid}",
              pickerIds: {pickers}
            }});
          </script>
        </div>
        """
        return mark_safe(html_output)

    @staticmethod
    def _default_colour(i: int) -> str:  # matches demo defaults
        defaults = ["#000000", "#ff0000", "#00ff00",
                    "#0000ff", "#ff00ff", "#ffa500"]
        return defaults[i]

    class Media:
        css = {"all": ("byefrontend/css/code_box.css",)}
        js = ("byefrontend/js/code_box.js",)


@ChildBuilderRegistry.register(CodeBoxConfig)
def _build_codebox(cfg: CodeBoxConfig, parent):
    return CodeBoxWidget(config=cfg, parent=parent)
