# ── src/byefrontend/configs/binary.py ──────────────────────────────────
"""
Binary-choice widgets (checkbox / radio-button) – *immutable* configs.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class CheckBoxConfig(WidgetConfig):
    """
    Immutable configuration for :class:`~byefrontend.widgets.CheckBoxWidget`.

    * ``checked`` – initial state.
    * ``label``   – text rendered next to the box (optional).
    """
    checked: bool = False
    label: str | None = None


@dataclass(frozen=True, slots=True)
class RadioConfig(WidgetConfig):
    """
    Immutable configuration for :class:`~byefrontend.widgets.RadioWidget`.

    * ``value``      – the value submitted when selected.
    * ``checked``    – initial state.
    * ``group_name`` – the HTML *name* attribute so related radios share a group.
    * ``label``      – text rendered next to the button (optional).
    """
    value: str = ""
    checked: bool = False
    group_name: str = "radio"
    label: str | None = None
