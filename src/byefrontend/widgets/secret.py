# src/byefrontend/widgets/secret.py
"""
Secret-field widget that now re-uses CharInputWidget for the
<label><input …></label> portion so both widgets stay visually
and semantically aligned.
"""
from __future__ import annotations

from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .char_input import CharInputWidget                # NEW
from .base import BFEBaseWidget, BFEBaseFormWidget
from ..builders   import ChildBuilderRegistry
from ..configs    import SecretToggleConfig
from ..configs.input import TextInputConfig            # NEW


class SecretToggleCharWidget(BFEBaseFormWidget):
    DEFAULT_CONFIG = SecretToggleConfig()
    aria_label     = "Toggle Secret Field Visibility"

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config

        # ── build the *inner* CharInputWidget --------------------------
        base_id   = f"secret-field_{self.id}"          # deterministic for toggle JS
        char_cfg  = TextInputConfig.build(
            html_id     = base_id,                    # ensure the IDs match the toggle
            label       = cfg.label or name,
            placeholder = cfg.placeholder,
            required    = cfg.required,
            input_type  = "password",                 # crucial difference vs. CharInput
            is_in_form  = cfg.is_in_form,
            classes     = ("secret-entry-field",),    # re-use existing styling
        )
        char_widget = CharInputWidget(config=char_cfg, parent=self)

        # Render <label><input></label> block
        inner_html = char_widget.render(name, value, attrs=attrs, renderer=renderer)

        # ── eye-toggle button ------------------------------------------
        toggle_html = (
            f'<button type="button" class="secret-entry-toggle" '
            f'data-bs-toggle="password" '
            f'data-target="#{base_id}" '
            f'data-icon="#icon_{base_id}" '
            f'aria-label="{self.aria_label}">'
            f'  <i class="eye-icon eye-closed" id="icon_{base_id}"></i>'
            f'</button>'
        )

        # Insert toggle right before the wrapper’s closing tag
        final_html = inner_html.replace("</div>", f"{toggle_html}</div>")

        # Replace the wrapper class so layouts stay unchanged
        final_html = final_html.replace("text-input-wrapper", "secret-input-wrapper", 1)

        return mark_safe(final_html)

    # ------------------------------------------------------------------ #
    #  Static media (unchanged)
    # ------------------------------------------------------------------ #
    class Media:
        css = {"all": ("byefrontend/css/secret_field.css",)}
        js  = ("byefrontend/js/secret_field.js",)


# Register with the builder registry
@ChildBuilderRegistry.register(SecretToggleConfig)
def _build_secret(cfg: SecretToggleConfig, parent):
    return SecretToggleCharWidget(config=cfg, parent=parent)
