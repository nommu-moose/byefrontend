from dataclasses import dataclass
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class LabelConfig(WidgetConfig):
    text: str = ""
    html_for: str | None = None
    tag: str = "label"       # could be "span", "strong", etc.
