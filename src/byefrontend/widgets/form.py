"""
Bye-Frontend composite form widget – glues Django’s Form plumbing to the
normal widget rendering & media aggregation system.
"""

from __future__ import annotations

import itertools
from types import SimpleNamespace
from typing import Any, Mapping

from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.crypto import get_random_string

from .base import BFEBaseWidget
from ..builders import build_children, ChildBuilderRegistry
from ..configs.form import FormConfig
from ..configs.file_upload import FileUploadConfig
from ..widgets.file_upload import FileUploadWidget

# ── helper: widget → field mapping ------------------------------------
WIDGET_TO_FIELD = {
    "CharInputWidget":  forms.CharField,
    "SecretToggleCharWidget": forms.CharField,
    "DatePickerWidget": forms.DateField,
    "DropdownWidget":   forms.ChoiceField,
    "CheckBoxWidget":   forms.BooleanField,
    "RadioGroupWidget": forms.ChoiceField,
    "FileUploadWidget": forms.FileField,  # will set required=False below
    "TextEditorWidget": forms.CharField,
}


class BFEFormWidget(forms.Form, BFEBaseWidget):
    DEFAULT_CONFIG = FormConfig()
    aria_label = "Composite Form Widget"

    # ----------------------------------------------------- construction
    def __init__(
        self,
        *,
        config: FormConfig | None = None,
        parent: BFEBaseWidget | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        request=None,                 # optional: forward to render() for CSRF
        **form_kwargs,
    ):
        self._request = request
        BFEBaseWidget.__init__(self, config=config, parent=parent)  # BFEBaseWidget
        prefix = config.prefix if config else None
        forms.Form.__init__(self, data=data, files=files, prefix=prefix, **form_kwargs)

        # realise child widgets
        self._children = build_children(self, self.cfg.children)
        self._build_fields()

    # shorthand
    cfg = property(lambda self: self.config)
    children = property(lambda self: self._children)

    def render(self, name: str = None, value: object = None, attrs=None, renderer=None, **kwargs):
        """
        todo: not comfortable with this, but for now the best solution I could figure out without reordering the MRO
        Ensure that the rendering logic from BFEBaseWidget is used,
        which in turn calls this class's _render method.
        """
        return BFEBaseWidget.render(self, name=name, value=value, attrs=attrs, renderer=renderer, **kwargs)

    # -------------------------------------------------------- field glue
    def _build_fields(self):
        """
        Create a matching Django Field for every child widget **without**
        giving Django our custom widget instance (it isn’t deepcopy-able
        and isn’t needed for form rendering/validation anyway).
        """
        for name, widget in self.children.items():
            if name in self.fields:        # allow subclass overrides
                continue

            field_cls = WIDGET_TO_FIELD.get(type(widget).__name__,
                                            forms.CharField)

            # pull basic requirements/choices from the BFE widget
            kwargs = {
                "required": getattr(widget, "required", True)
            }
            if field_cls is forms.ChoiceField and hasattr(widget, "cfg"):
                kwargs["choices"] = getattr(widget.cfg, "choices", [])

            if isinstance(widget, FileUploadWidget):
                kwargs["required"] = False     # file inputs are optional

            # ‼️  IMPORTANT:  do **not** pass `widget=widget` here
            self.fields[name] = field_cls(**kwargs)

    # --------------------------------------------------------- rendering
    def _render(self, *_, **__):
        cfg = self.cfg
        enctype = ""
        if cfg.multipart or any(isinstance(w, FileUploadWidget) for w in self.children.values()):
            enctype = ' enctype="multipart/form-data"'

        csrf_input = ""
        if cfg.csrf:
            # `self._request` is now a SimpleNamespace with the token we
            # stashed away in `_strip_request()`, but fall back to
            # `django.middleware.csrf.get_token()` just in case.
            from django.middleware.csrf import get_token
            token = getattr(self._request, "csrf_token", None) or get_token(self._request)
            csrf_input = (
                f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">'
            )

        inner = "".join(
            child.render(name=child_name)
            for child_name, child in self.children.items()
        )
        errors_html = self._render_errors()

        btn = '<button type="submit" class="bfe-btn">Send feedback</button>'

        return mark_safe(
            f'<form id="{self.id}" action="{cfg.action}" method="{cfg.method}"{enctype} '
            f'class="bfe-form-widget">'
            f'{csrf_input}{errors_html}{inner}{btn}'
            f'</form>'
        )

    # basic error list (can be styled by .bfe-error-list)
    def _render_errors(self):
        if not self.errors:
            return ""
        items = "".join(f"<li>{e}</li>" for e in itertools.chain.from_iterable(self.errors.values()))
        return f'<ul class="bfe-error-list">{items}</ul>'

    # ----------------------------------------------------------- media
    # ----------------------------------------------------------- media
    @property
    def media(self):
        """
        Merge three sources seamlessly:

        • static files declared by *this* class     → via Form.media
        • static files contributed by child widgets → via BFEBaseWidget.media
        • static files contributed by widgets used as Django Fields
          (identical to a normal Form)              → via Form.media
        """
        bfe_media = BFEBaseWidget.media.fget(self)  # children
        form_media = forms.Form.media.fget(self)  # Django’s normal path
        return bfe_media + form_media

    class Media:
        css = {"all": ("byefrontend/css/form.css",)}
        js = ()


# automatic builder registration
@ChildBuilderRegistry.register(FormConfig)
def _build_form(cfg: FormConfig, parent):
    return BFEFormWidget(config=cfg, parent=parent)
