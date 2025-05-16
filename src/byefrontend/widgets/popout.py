"""
Pop-out / modal widget that now ships with an embedded *Python* CodeBox.

• Clicking the trigger button opens a <dialog>.
• Inside the dialog you’ll find a syntax-highlighted code editor
  powered by CodeBoxWidget.
"""

from __future__ import annotations

import uuid
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.popout import PopOutConfig

# NEW: import the code-box family
from ..widgets.code_box import CodeBoxWidget
from ..configs.code_box import CodeBoxConfig


class PopOut(BFEBaseWidget):
    DEFAULT_CONFIG = PopOutConfig()
    aria_label     = "Open pop-out dialog"

    # ──────────────────────────────────────────────────────────
    #  Construction – build the code-box once and keep it as a child
    # ──────────────────────────────────────────────────────────
    def __init__(self,
                 config: PopOutConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        super().__init__(config=config, parent=parent, **overrides)

        code_cfg       = CodeBoxConfig(language="python", rows=12, cols=80,
                                       placeholder="# Write Python here…")
        self._children = {
            "code_box": CodeBoxWidget(config=code_cfg, parent=self)
        }

    # shorthand
    code_box = property(lambda self: self.children["code_box"])

    # ──────────────────────────────────────────────────────────
    #  Rendering
    # ──────────────────────────────────────────────────────────
    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg   = self.config
        uid   = uuid.uuid4().hex
        title = cfg.title or "Code Editor"

        # If caller supplies *value* we drop it into the editor, otherwise blank
        code_html = self.code_box.render(name=f"{uid}_code", value=value or "")

        dialog_html = f"""
        <button type="button"
                data-popout-open="{uid}"
                class="bfe-btn">{cfg.trigger_text}</button>

        <dialog id="{uid}" class="bfe-popout" aria-modal="true">
          <form method="dialog" class="bfe-popout-form">
            <header class="bfe-popout-header">
              <h3>{title}</h3>
              <button type="button"
                      data-popout-close="{uid}"
                      class="bfe-popout-close"
                      aria-label="Close">&times;</button>
            </header>

            <div class="bfe-popout-body">
              {code_html}
            </div>

            <menu class="bfe-popout-footer">
              <button type="submit"
                      data-popout-close="{uid}"
                      class="bfe-btn bfe-btn--primary">OK</button>
            </menu>
          </form>
        </dialog>
        """
        return mark_safe(dialog_html)

    # Static assets for the *dialog* itself.
    # Code-box assets are inherited automatically via children → media.
    class Media:
        css = {"all": ("byefrontend/css/popout.css",)}
        js  = ("byefrontend/js/popout.js",)
