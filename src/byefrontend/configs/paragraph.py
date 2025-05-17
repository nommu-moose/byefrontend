from __future__ import annotations
from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class ParagraphConfig(WidgetConfig):
    """
    Immutable configuration for ParagraphWidget.

    • text   – inner text/HTML for the <p> element
    • align  – optional text-alignment: "left", "center", "right", "justify"
    • italic – render the paragraph in italics when True
    """

    text: str = ""
    align: str | None = None
    italic: bool = False
