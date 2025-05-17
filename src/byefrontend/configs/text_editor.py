from dataclasses import dataclass

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class TextEditorConfig(WidgetConfig):
    """
    Immutable settings for the rich-text editor.

    • value           – **initial HTML** shown in the editor (may contain tags)
    • placeholder     – first hint shown in the area (only when editor is empty)
    • min_height_rem  – editable region height in *rem*
    • toolbar_compact – True ➜ toolbar becomes one-line scrollable
    """
    # 🆕  this is what allows us to inject server-side content
    value: str | None = None

    placeholder: str = "Type here…"
    min_height_rem: float = 20.0
    toolbar_compact: bool = False
