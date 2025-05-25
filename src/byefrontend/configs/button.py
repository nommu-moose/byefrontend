from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class ButtonConfig(WidgetConfig):
    text: str = "Click me"

    # look & behaviour
    classes: Tuple[str, ...] = ("bfe-btn",)
    disabled: bool = False
    button_type: str = "button"  # "button" | "submit" | "reset"
