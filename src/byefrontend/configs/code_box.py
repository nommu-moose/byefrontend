"""
Configuration for a monospaced <textarea> with optional syntax highlighting.
"""

from dataclasses import dataclass, field
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class CodeBoxConfig(WidgetConfig):
    placeholder: str | None = None
    language: str = "text"     # e.g. "python", "json" – drives CSS class
    rows: int = 10
    cols: int = 60
    readonly: bool = False
    disabled: bool = False
    value: str | None = None
