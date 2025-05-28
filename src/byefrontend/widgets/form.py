from __future__ import annotations
import itertools
from typing import Any, Mapping
from django import forms
from django.utils.safestring import mark_safe
from django.middleware.csrf import get_token
from .base import BFEBaseWidget
from ..builders import build_children, ChildBuilderRegistry
from ..configs.form import FormConfig
from ..widgets.file_upload import FileUploadWidget
from logging import getLogger
log = getLogger(__name__)


WIDGET_TO_FIELD = {
    "CharInputWidget":  forms.CharField,
    "SecretToggleCharWidget": forms.CharField,
    "DatePickerWidget": forms.DateField,
    "DropdownWidget":   forms.ChoiceField,
    "CheckBoxWidget":   forms.BooleanField,
    "RadioGroupWidget": forms.ChoiceField,
    "FileUploadWidget": forms.FileField,
    "TextEditorWidget": forms.CharField,
}


class BFEFormWidget(forms.Form, BFEBaseWidget):
    """
    Bye-Frontend composite form widget – glues Django’s Form plumbing to the
    normal widget rendering & media aggregation system.
    does not need manual addition of submit button
    """
    DEFAULT_CONFIG = FormConfig()
    aria_label = "Composite Form Widget"

    def __init__(
        self,
        *,
        config: FormConfig | None = None,
        parent: BFEBaseWidget | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        request=None,  # optional: forward to render() for CSRF
        **form_kwargs,
    ):
        self._request = request
        BFEBaseWidget.__init__(self, config=config, parent=parent)
        prefix = config.prefix if config else None
        forms.Form.__init__(self, data=data, files=files, prefix=prefix, **form_kwargs)

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

    def _build_fields(self):
        """
        create a matching Django Field for every child widget **without**
        giving Django our custom widget instance (deepcopy breaks if we try, not needed for rendering/validation anyway)
        """
        for name, widget in self.children.items():
            if name in self.fields:  # allow subclass overrides
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
                kwargs["required"] = False  # file inputs are optional - remember why this is the case?

            self.fields[name] = field_cls(**kwargs)

    def _initial_for(self, field_name: str):
        """
        Decide which value the *child widget* called *field_name* should
        receive when we render the form.

        Priority:
        1.  If the form is bound      – whatever was just submitted.
        2.  `initial={...}` argument  – passed to the Form’s constructor.
        3.  The Django Field’s own    `.initial` attribute (if any).
        4.  `None`                    – fall back to the widget’s config.
        """
        if self.is_bound:
            return self.data.get(field_name, None)

        if field_name in self.initial:
            return self.initial[field_name]

        fld = self.fields.get(field_name)
        return getattr(fld, "initial", None)

    def _render(self, *_, **__):
        cfg = self.cfg
        log.debug(
            "BFEFormWidget: csrf=%s  multipart=%s  request=%s",
            cfg.csrf,
            cfg.multipart,
            bool(self._request),
        )
        enctype = ""
        if cfg.multipart or any(isinstance(w, FileUploadWidget) for w in self.children.values()):
            enctype = ' enctype="multipart/form-data"'

        csrf_input = ""
        if cfg.csrf:
            token = getattr(self._request, "csrf_token", None) or get_token(self._request)
            csrf_input = (
                f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">'
            )

        inner = "".join(
            child.render(
                name=child_name,
                value=self._initial_for(child_name)
            )
            for child_name, child in self.children.items()
        )
        errors_html = self._render_errors()

        btn = '<button type="submit" class="bfe-btn">Submit</button>'

        return mark_safe(
            f'<form id="{self.id}" action="{cfg.action}" method="{cfg.method}"{enctype} '
            f'class="bfe-form-widget">'
            f'{csrf_input}{errors_html}{inner}{btn}'
            f'</form>'
        )

    # basic error list styled by .bfe-error-list
    def _render_errors(self):
        if not self.errors:
            return ""
        items = "".join(f"<li>{e}</li>" for e in itertools.chain.from_iterable(self.errors.values()))
        return f'<ul class="bfe-error-list">{items}</ul>'

    @property
    def media(self):
        """
        Merge three sources seamlessly:

        - static files declared by *this* class     -> via Form.media
        - static files contributed by child widgets -> via BFEBaseWidget.media
        - static files contributed by widgets used as Django Fields
          (identical to a normal Form)              -> via Form.media
        """
        bfe_media = BFEBaseWidget.media.fget(self)  # children
        form_media = forms.Form.media.fget(self)  # django’s normal path
        return bfe_media + form_media

    class Media:
        css = {"all": ("byefrontend/css/form.css",)}
        js = ()


@ChildBuilderRegistry.register(FormConfig)
def _build_form(cfg: FormConfig, parent):
    return BFEFormWidget(config=cfg, parent=parent)
