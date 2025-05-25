from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, Tuple
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class DropdownConfig(WidgetConfig):
    """
    Immutable settings for DropdownWidget.

    - choices   – sequence of (“value”, “label”) pairs
    - selected  – pre-selected value or None
    - placeholder – optional disabled first row (“Choose …”)
    - is_in_form – suppress outer <label> when inside a Django Form
    """
    choices: Sequence[Tuple[str, str]] = field(default_factory=tuple)
    selected: str | None = None
    placeholder: str | None = None
    is_in_form: bool = False
    disabled: bool = False
