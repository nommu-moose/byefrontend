from dataclasses import dataclass
from .base import WidgetConfig     # existing helper

@dataclass(frozen=True, slots=True)
class TextEditorConfig(WidgetConfig):
    """
    Immutable settings for the rich-text editor.

    • placeholder      – first hint shown in the area
    • min_height_rem   – editable region height in *rem*
    • toolbar_compact  – True ➜ toolbar becomes one-line scrollable
    """
    placeholder: str = "Type here…"
    min_height_rem: float = 20.0
    toolbar_compact: bool = False
