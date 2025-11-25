"""
ColumnsConfig - Configuration for multi-column layouts.

Uses CSS Grid for flexible column arrangements with
configurable ratios.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class ColumnsConfig(WidgetConfig):
    """
    Configuration for a multi-column layout using CSS Grid.
    
    Each item in `columns` is a WidgetConfig that will be
    rendered in its own column. Use `ratios` to control
    relative column widths.
    
    Example:
        ColumnsConfig(
            columns=(
                SectionConfig(title="Left", fields=('name',)),
                SectionConfig(title="Right", fields=('email', 'phone')),
            ),
            ratios=(1, 2),  # Right column is 2x wider
        )
    """
    # Child configs for each column
    columns: Tuple[WidgetConfig, ...] = ()
    
    # Relative width ratios (e.g., (1, 2) = 1fr 2fr)
    # If empty, defaults to equal widths (1fr each)
    ratios: Tuple[int, ...] = ()
    
    # Gap between columns
    gap: float = 1.0  # in rem
    
    # Responsive behavior
    stack_below: int = 768  # Stack vertically below this width (px), 0 to disable
    
    # Vertical alignment of column contents
    align: str = "start"  # "start" | "center" | "end" | "stretch"

