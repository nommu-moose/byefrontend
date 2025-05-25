from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class ThumbnailConfig(WidgetConfig):
    src: str = ""
    alt: str = ""
    size_px: int = 48
