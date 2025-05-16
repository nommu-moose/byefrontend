# NEW FILE - immutable config for a group of radios
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, Tuple

from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class RadioGroupConfig(WidgetConfig):
    """
    Immutable settings for RadioGroupWidget.

    • ``name``      – the shared HTML *name* attribute
    • ``choices``   – sequence of (value, label) pairs
    • ``selected``  – value pre-checked (or None)
    • ``layout``    – "inline" or "stacked"
    """
    # ── optional card wrapper ──────────────────────────────────
    title: str | None = None     # e.g. "Pick a flavour"
    level: int = 3          # <h3> by default (1-6 allowed)

    name: str = "radio_group"
    choices: Sequence[Tuple[str, str]] = (("A", "Choice A"), ("B", "Choice B"))
    selected: str | None = None
    layout: str = "inline"
