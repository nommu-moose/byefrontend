# src/byefrontend/configs/popout.py
from dataclasses import dataclass
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class PopOutConfig(WidgetConfig):
    trigger_text: str = "Open"
    title: str = "Dialog"
    width_px: int = 480
    height_px: int = 360
    blur_background: bool = True
