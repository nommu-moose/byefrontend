# src/byefrontend/configs/title.py
from dataclasses import dataclass
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class TitleConfig(WidgetConfig):
    text: str = "Untitled"
    level: int = 1               # h1 … h6
