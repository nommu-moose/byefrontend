from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class TextEditorConfig(WidgetConfig):
    """
    Immutable settings for the rich-text editor.

    - value – **initial HTML** rendered in the editor
    - placeholder – initial hint shown in empty area
    - min_height_rem – editable region height in rem
    - toolbar_compact – True -> toolbar becomes one-line scrollable
    """
    value: str | None = None
    placeholder: str = "Type here…"
    min_height_rem: float = 20.0
    toolbar_compact: bool = False
