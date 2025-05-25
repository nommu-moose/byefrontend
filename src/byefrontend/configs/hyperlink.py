from dataclasses import dataclass
from typing import Sequence, Tuple
from .base import WidgetConfig


@dataclass(slots=True, frozen=True)
class HyperlinkConfig(WidgetConfig):
    text: str = ""
    link: str = "#"
    classes: Tuple[str, ...] = ("btn-success",)
    reverse_args: Sequence[str] = tuple()
    view_visible: bool = True
    edit_visible: bool = True
