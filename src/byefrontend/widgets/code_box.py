from django.forms.widgets import Widget
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.code_box import CodeBoxConfig


class CodeBoxWidget(BFEBaseWidget, Widget):
    """
    A monospace text-area that plays nicely with your immutable configs.
    """

    DEFAULT_CONFIG = CodeBoxConfig()

    def __init__(self, config: CodeBoxConfig | None = None, *, parent=None, **overrides):
        super().__init__(config=config, parent=parent, **overrides)

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        final_val = escape(value if value is not None else (cfg.value or ""))
        lang_cls = f"language-{cfg.language}" if cfg.language else ""
        readonly = " readonly" if cfg.readonly else ""
        disabled = " disabled" if cfg.disabled else ""
        placeholder = f' placeholder="{escape(cfg.placeholder)}"' if cfg.placeholder else ""
        rows = f' rows="{cfg.rows}"'
        cols = f' cols="{cfg.cols}"'

        html = (
            f'<textarea id="{self.id}" '
            f'class="code-box {lang_cls} { " ".join(cfg.classes) }"'
            f'{rows}{cols}{readonly}{disabled}{placeholder}>'
            f'{final_val}'
            '</textarea>'
        )
        return mark_safe(html)

    class Media:
        css = {"all": ("byefrontend/css/code_box.css",)}
        js = ("byefrontend/js/code_box.js",)
