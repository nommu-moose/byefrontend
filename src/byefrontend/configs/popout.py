# src/byefrontend/configs/popout.py
from dataclasses import dataclass
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class PopOutConfig(WidgetConfig):
    trigger_text: str = "Open"
    title: str = "Dialog"
    width_px: int = 1600
    height_px: int = 900
    blur_background: bool = True
