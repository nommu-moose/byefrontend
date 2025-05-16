# ── src/byefrontend/configs/datepicker.py ─────────────────────────
from __future__ import annotations
from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class DatePickerConfig(WidgetConfig):
    """
    Immutable settings for DatePickerWidget.

    • placeholder – hint text shown when empty
    • min_date / max_date – ISO dates (“YYYY-MM-DD”) restricting the picker
    • is_in_form – skip rendering a <label> when used inside Django Forms
    • readonly / disabled – HTML flags, mirror CharInputWidget behaviour
    """
    placeholder: str | None = None
    min_date: str | None = None
    max_date: str | None = None
    is_in_form: bool = False
    readonly: bool = False
    disabled: bool = False
