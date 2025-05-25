from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class CardConfig(WidgetConfig):
    #  optional heading
    title: str | None = None  # card heading
    level: int = 3  # HTML <h> level

    # nested widgets (name: WidgetConfig)
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
