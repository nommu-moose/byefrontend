from __future__ import annotations
from django.utils.safestring import mark_safe
from .char_input import CharInputWidget
from .base import BFEBaseWidget, BFEFormCompatibleWidget
from ..builders import ChildBuilderRegistry
from ..configs import SecretToggleConfig
from ..configs.input import TextInputConfig


class SecretToggleCharWidget(BFEFormCompatibleWidget):
    DEFAULT_CONFIG = SecretToggleConfig()
    aria_label = "Toggle Secret Field Visibility"

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        cfg = self.config

        base_id = f"secret-field_{self.id}"
        char_cfg = TextInputConfig.build(
            html_id = base_id,
            label = cfg.label or name,
            placeholder = cfg.placeholder,
            required = cfg.required,
            input_type = "password",
            is_in_form = cfg.is_in_form,
            classes = ("secret-entry-field",),
        )
        char_widget = CharInputWidget(config=char_cfg, parent=self)

        inner_html = char_widget.render(name, value, attrs=attrs, renderer=renderer)

        # eye-toggle button
        toggle_html = (
            f'<button type="button" class="secret-entry-toggle" '
            f'data-bs-toggle="password" '
            f'data-target="#{base_id}" '
            f'data-icon="#icon_{base_id}" '
            f'aria-label="{self.aria_label}">'
            f'  <i class="eye-icon eye-closed" id="icon_{base_id}"></i>'
            f'</button>'
        )

        final_html = inner_html.replace("</div>", f"{toggle_html}</div>")

        final_html = final_html.replace("text-input-wrapper", "secret-input-wrapper", 1)

        return mark_safe(final_html)

    class Media:
        css = {"all": ("byefrontend/css/secret_field.css",)}
        js = ("byefrontend/js/secret_field.js",)


@ChildBuilderRegistry.register(SecretToggleConfig)
def _build_secret(cfg: SecretToggleConfig, parent):
    return SecretToggleCharWidget(config=cfg, parent=parent)
