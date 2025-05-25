from __future__ import annotations
import uuid
from typing import Any, Mapping
from django.utils.safestring import mark_safe
from django.forms.widgets import Media
from .base import BFEBaseWidget
from ..configs import WidgetConfig
from ..configs.popout import PopOutConfig
from ..builders import ChildBuilderRegistry
from ..widgets.code_box import CodeBoxWidget
from ..configs.code_box import CodeBoxConfig


class PopOut(BFEBaseWidget):
    """
    fully generic pop-out / modal dialog

    -  Accepts *any* Bye-Frontend widget as its content
    -  Exposes that child through the normal `.children` mapping, so the automatic media collector picks up all CSS/JS.
    -  Still falls back to a Python CodeBox when no explicit content is
       supplied, preserving legacy behaviour.

    Usage
    >>> pop = PopOut(                       # “Hello” in a modal
    ...     content=ParagraphWidget(text="Hello world!")
    ... )
    """
    DEFAULT_CONFIG = PopOutConfig()
    aria_label = "Open pop-out dialog"

    def __init__(self,
                 *,
                 config: PopOutConfig | None = None,
                 content: BFEBaseWidget | WidgetConfig | None = None,
                 parent: BFEBaseWidget | None = None,
                 **overrides):
        """
        Parameters
        content :
            - *None*  -> a small Python CodeBox is inserted as before.
            - A **widget instance** -> used verbatim.
            - A **WidgetConfig**   -> we instantiate it for you.
        """
        super().__init__(config=config, parent=parent, **overrides)

        # determine the inner widget
        if content is None:  # old default, todo: once clients upgraded remove this
            cb_cfg = CodeBoxConfig(language="python", rows=12, cols=80, placeholder="# Write Python here…")
            content_widget = CodeBoxWidget(config=cb_cfg, parent=self)

        elif hasattr(content, "_render"):  # already widget
            content.parent = self
            content_widget = content

        else:  # assume config
            content_widget = ChildBuilderRegistry.build(content, self)

        self._children: Mapping[str, BFEBaseWidget] = {
            "content": content_widget
        }

    # shorthand
    cfg = property(lambda self: self.config)
    _content = property(lambda self: self.children["content"])

    def _render(self, *_, **__) -> str:
        uid = uuid.uuid4().hex
        title = self.cfg.title or "Dialog"
        inner_html = self._content.render()

        dialog_html = f"""
                <button type="button"
                        data-popout-open="{uid}"
                        class="bfe-btn">{self.cfg.trigger_text}</button>

                <dialog id="{uid}" class="bfe-popout" aria-modal="true"
                        style="--popout-width:{self.cfg.width_px}px; --popout-height:{self.cfg.height_px}px;">
                  <form method="dialog" class="bfe-popout-form">
                    <header class="bfe-popout-header">
                      <h3>{title}</h3>
                      <button type="button"
                              data-popout-close="{uid}"
                              class="bfe-popout-close"
                              aria-label="Close">&times;</button>
                    </header>

                    <div class="bfe-popout-body">
                      {inner_html}
                    </div>

                    <menu class="bfe-popout-footer">
                      <button type="submit"
                              data-popout-close="{uid}"
                              class="bfe-btn">OK</button>
                    </menu>
                  </form>
                </dialog>
                """
        return mark_safe(dialog_html)

    class Media:
        css = {"all": ("byefrontend/css/popout.css",)}
        js = ("byefrontend/js/popout.js",)


@ChildBuilderRegistry.register(PopOutConfig)
def _build_popout(cfg: PopOutConfig, parent):
    return PopOut(config=cfg, parent=parent)
