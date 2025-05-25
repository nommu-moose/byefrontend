from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class InlineGroupConfig(WidgetConfig):
    """
    pure layout container: renders all `children` side-by-side in a flex row.
    does no form handling itself
    - children – mapping “name -> WidgetConfig”
    - gap – flex-gap in rem
    - wrap – items wrap to next line
    """
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
    gap: float = 0.5  # in rem
    wrap: bool = True
