# src/byefrontend/configs/document_viewer.py
from dataclasses import dataclass
from .base import WidgetConfig

@dataclass(frozen=True, slots=True)
class DocumentViewerConfig(WidgetConfig):
    """
    • file_url   – absolute or MEDIA-relative URL
    • file_type  – optional override ("pdf", "docx", "xlsx" …);
                   if left None we'll infer from the extension
    • height_rem – iframe height
    """
    file_url: str = ""
    file_type: str | None = None
    height_rem: float = 48.0
