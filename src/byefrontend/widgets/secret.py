# -----------------------------------------------------------------------------#
#  SecretToggleCharWidget – config-driven re-implementation
# -----------------------------------------------------------------------------#
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from . import LabelWidget
from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs import SecretToggleConfig, LabelConfig


class SecretToggleCharWidget(BFEBaseWidget, Widget):
    """
    Password/secret input with an *eye* toggle, driven entirely by an
    immutable :class:`SecretToggleConfig`.

    ➜  **Source-compatible**: legacy calls such as
        `SecretToggleCharWidget(attrs={…}, is_in_form=True)` still work
        because extra keyword arguments are merged into a private copy
        of *config* via :pyfunc:`dataclasses.replace`.
    """

    DEFAULT_CONFIG = SecretToggleConfig()
    aria_label = "Toggle Secret Field Visibility"

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self,
                 config: SecretToggleConfig | None = None,
                 *,
                 parent=None,
                 attrs: dict | None = None,
                 **overrides):
        """
        Parameters
        ----------
        config:
            A (possibly tweaked) :class:`SecretToggleConfig`.
        attrs:
            Raw HTML attributes forwarded verbatim to the underlying
            `<input>`.  Supplying *attrs* disables render caching for
            this instance (handled by :class:`BFEBaseWidget`).
        overrides:
            Legacy keyword tweaks merged into *config* so existing
            call-sites keep working.
        """
        if attrs is not None:
            overrides["attrs"] = attrs
        super().__init__(config=config, parent=parent, **overrides)

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config

        # ----- derive misc HTML bits ------------------------------------
        placeholder = cfg.placeholder or self.attrs.get("placeholder", "")
        required    = " required" if cfg.required else ""
        label_txt   = cfg.label or name

        # A stable, cache-friendly ID (self.id is already unique)
        base_id = f"secret-field_{self.id}"

        # ----- build <input> -------------------------------------------
        value_attr = ""
        if value is not None:
            value_attr = f' value="{value}"'
        elif (dv := self.attrs.get("value")) is not None:
            value_attr = f' value="{dv}"'

        input_html = (
            f'<input type="password" id="{base_id}" name="{name}" '
            f'class="secret-entry-field"'
            f'{f" placeholder=\"{placeholder}\"" if placeholder else ""}'
            f'{required}{value_attr}>'
        )

        # ----- build toggle button --------------------------------------
        toggle_html = (
            f'<button type="button" class="secret-entry-toggle" '
            f'data-bs-toggle="password" '
            f'data-target="#{base_id}" '
            f'data-icon="#icon_{base_id}" '
            f'aria-label="{self.aria_label}">'
            f'  <i class="eye-icon eye-closed" id="icon_{base_id}"></i>'
            f'</button>'
        )

        # ----- use *LabelWidget* instead of hand-rolled <label> ---------
        if not cfg.is_in_form:
            label_cfg    = LabelConfig(text=label_txt, html_for=base_id)
            label_widget = LabelWidget(config=label_cfg, parent=self)
            label_html   = label_widget.render()
        else:
            label_html   = ""  # Django form machinery will supply its own

        # ----- final markup ---------------------------------------------
        return mark_safe(
            f'<div class="secret-input-wrapper">'
            f'  {label_html}'
            f'  {input_html}'
            f'  {toggle_html}'
            f'</div>'
        )

    # ------------------------------------------------------------------ #
    #  Static media declaration (unchanged)
    # ------------------------------------------------------------------ #
    class Media:
        css = {"all": ("byefrontend/css/secret_field.css",)}
        js  = ("byefrontend/js/secret_field.js",)

@ChildBuilderRegistry.register(SecretToggleConfig)
def _build_secret(cfg: SecretToggleConfig, parent):
    return SecretToggleCharWidget(config=cfg, parent=parent)
