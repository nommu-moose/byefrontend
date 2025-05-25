from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class DocumentLinkConfig(WidgetConfig):
    file_url: str = ""
    label: str = "Download"
    show_size: bool = True
