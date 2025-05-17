# src/byefrontend/widgets/document_link.py
from pathlib import Path
from django.conf import settings
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.document_link import DocumentLinkConfig
from ..builders import ChildBuilderRegistry

class DocumentLinkWidget(BFEBaseWidget):
    DEFAULT_CONFIG = DocumentLinkConfig()
    aria_label = "Download file"

    cfg = property(lambda self: self.config)

    def _render(self, *_, **__):
        url  = self._abs(self.cfg.file_url)
        size = self._size_human(url) if self.cfg.show_size else ""
        icon = "📄"  # swap for nicer SVG if you like

        return mark_safe(
            f'<a id="{self.id}" href="{url}" class="bfe-btn" download>'
            f'{icon} {self.cfg.label}{size}</a>'
        )

    def _abs(self, p: str) -> str:
        return p if p.startswith(("http://", "https://", "/")) else settings.MEDIA_URL + p

    def _size_human(self, url: str) -> str:
        try:
            # MEDIA_ROOT + relative path → size on disk
            from django.core.files.storage import default_storage
            rel = url.removeprefix(settings.MEDIA_URL).lstrip("/")
            size = default_storage.size(rel)
            for unit in (" B", " KB", " MB", " GB"):
                if size < 1024: return f" ({size:.0f}{unit})"
                size /= 1024
        except Exception:
            pass
        return ""

    class Media:
        css = {}
        js = ()

@ChildBuilderRegistry.register(DocumentLinkConfig)
def _build_doclink(cfg: DocumentLinkConfig, parent):
    return DocumentLinkWidget(config=cfg, parent=parent)
