from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class TagInputConfig(WidgetConfig):
    """Immutable configuration for TagInputWidget."""
    placeholder: str | None = None
    suggestions: Sequence[str] = field(default_factory=tuple)
    is_in_form: bool = False
