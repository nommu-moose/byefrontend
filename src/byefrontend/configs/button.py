"""
Immutable configuration for a generic <button> element.

The button re-uses the existing ``.bfe-btn`` look defined in
root.css, so it needs **no extra CSS** of its own.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class ButtonConfig(WidgetConfig):
    # ── button text & semantics ───────────────────────────────────────
    text: str = "Click me"
    button_type: str = "button"         # "button" | "submit" | "reset"

    # ── look & behaviour ─────────────────────────────────────────────
    classes: Tuple[str, ...] = ("bfe-btn",)   # re-use existing theme class
    disabled: bool = False
