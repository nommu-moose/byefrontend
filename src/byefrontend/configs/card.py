"""
Immutable configuration for CardWidget – a visual “wrapper” that
collects an optional heading and an arbitrary mapping of children.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping

from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class CardConfig(WidgetConfig):
    # ── optional heading ───────────────────────────────────────────────
    title: str | None = None          # card heading (plain text)
    level: int      = 3               # HTML <hₙ> level → 1–6

    # ── nested widgets (name ➜ WidgetConfig) ───────────────────────────
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
