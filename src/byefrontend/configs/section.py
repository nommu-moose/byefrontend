"""
SectionConfig - Configuration for collapsible, titled sections.

Used in model views to group fields together with optional
collapsible behavior.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Tuple

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class SectionConfig(WidgetConfig):
    """
    Configuration for a titled, optionally collapsible section.
    
    Can contain either:
    - `fields`: tuple of field names (resolved by BFEModelView)
    - `children`: explicit WidgetConfig children
    
    Both can be combined - fields are resolved first, then
    explicit children are added/override.
    
    Example:
        SectionConfig(
            title="Contact Information",
            fields=('name', 'email', 'phone'),
            collapsible=True,
        )
    """
    # Section heading
    title: str = ""
    level: int = 3  # HTML <h> level (1-6)
    
    # Field names to include (resolved from model by BFEModelView)
    fields: Tuple[str, ...] = ()
    
    # Explicit children (WidgetConfigs)
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
    
    # Collapse behavior
    collapsible: bool = False
    collapsed: bool = False  # Initial collapsed state
    
    # Styling
    bordered: bool = True  # Show border around section
    padded: bool = True  # Add internal padding

