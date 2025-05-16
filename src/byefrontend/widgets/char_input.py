from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget, BFEBaseFormWidget
from .label import LabelWidget
from ..configs.label import LabelConfig
from ..configs.input import TextInputConfig
from ..builders import ChildBuilderRegistry


class CharInputWidget(BFEBaseFormWidget):
    """
    A straightforward <input type="text"> field that mirrors the look-and-feel
    of SecretToggleCharWidget but without the eye-toggle or password masking.
    """
    DEFAULT_CONFIG = TextInputConfig()
    aria_label = "Text input"

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg        = self.config
        placeholder = cfg.placeholder or self.attrs.get("placeholder", "")
        required    = " required" if cfg.required else ""
        readonly    = " readonly" if getattr(cfg, "readonly", False) else ""
        disabled    = " disabled" if getattr(cfg, "disabled", False) else ""
        label_txt   = cfg.label or name

        base_id = self.id  # unique, stable

        # initial value precedence: explicit value > attrs["value"]
        val_attr = ""
        if value is not None:
            val_attr = f' value="{value}"'
        elif (dv := self.attrs.get("value")) is not None:
            val_attr = f' value="{dv}"'

        input_html = (
            f'<input type="{cfg.input_type}" id="{base_id}" name="{name}" '
            f'class="text-entry-field"'
            f'{f" placeholder=\"{placeholder}\"" if placeholder else ""}'
            f'{required}{readonly}{disabled}{val_attr}>'
        )

        if cfg.is_in_form:
            label_html = ""        # Django’s Form machinery handles <label>
        else:
            label_cfg   = LabelConfig(text=label_txt, html_for=base_id)
            label_html  = LabelWidget(config=label_cfg, parent=self).render()

        return mark_safe(
            f'<div class="text-input-wrapper">{label_html}{input_html}</div>'
        )

    class Media:          # styling is entirely optional – omit if unneeded
        css = {"all": ("byefrontend/css/secret_field.css",)}  # re-use existing look
        js  = ()


# -- Builder registration ----------------------------------------------------
@ChildBuilderRegistry.register(TextInputConfig)
def _build_char(cfg: TextInputConfig, parent):
    return CharInputWidget(config=cfg, parent=parent)
