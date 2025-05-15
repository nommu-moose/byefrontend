# src/byefrontend/widgets/multi_inline_form.py
"""
This is a *thin* façade; the heavy lifting (formsets, validation, etc.)
is left to Django Forms and/or your own business logic.
"""

from .base import BFEBaseWidget
from django.forms import formset_factory, Form
from django.utils.safestring import mark_safe


class MultiInlineForm(BFEBaseWidget):
    """
    Wraps a Django formset so that each item renders inline.
    Accepts a `base_form` argument at runtime; therefore no frozen Config
    is needed (yet).  Feel free to extend with its own Config later.
    """

    def __init__(self, base_form: type[Form], *, extra=1, can_delete=True, parent=None):
        super().__init__(parent=parent)
        self.formset_cls = formset_factory(base_form, extra=extra, can_delete=can_delete)

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        formset = self.formset_cls()
        forms_html = "".join(form.as_p() for form in formset)
        return mark_safe(f'<div id="{self.id}" class="bfe-inline-formset">{forms_html}</div>')

    class Media:
        css = {"all": ("byefrontend/css/inline_formset.css",)}
