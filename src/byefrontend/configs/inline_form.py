from __future__ import annotations
from dataclasses import dataclass, field

from .form import FormConfig


@dataclass(frozen=True, slots=True)
class InlineFormConfig(FormConfig):
    """Immutable settings for **inline** forms.
    - gap   – horizontal / vertical gap between widgets (rem)
    - wrap  – wrap onto the next row (`True`) or keep a single line (`False`)
    """
    gap: float = 0.5
    wrap: bool = True
