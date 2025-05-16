from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class InlineGroupConfig(WidgetConfig):
    """
    Pure *layout* container: renders all `children` side-by-side in a flex row.
    It does **no** form handling – that’s for a higher-level helper.

    • children – mapping “name ➜ WidgetConfig”
    • gap      – flex-gap in *rem*
    • wrap     – True: items wrap to next line; False: single line
    """
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
    gap: float = 0.5      # in rem
    wrap: bool = True
