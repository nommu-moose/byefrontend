
# src/byefrontend/configs/inline_form.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping

from .form import FormConfig      # re-use every field from the normal form
                                   # and just add the layout tweaks

@dataclass(frozen=True, slots=True)
class InlineFormConfig(FormConfig):
    """Immutable settings for **inline** forms.

    • gap   – horizontal / vertical gap between widgets (rem)
    • wrap  – wrap onto the next row (`True`) or keep a single line (`False`)
    """
    gap:  float = 0.5
    wrap: bool  = True
