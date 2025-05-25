# ── top-of-file imports ───────────────────────────────────────────────
from __future__ import annotations

from django.conf import settings
from django.forms.widgets import Media
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.document_viewer import DocumentViewerConfig


class DocumentViewerWidget(BFEBaseWidget):
    DEFAULT_CONFIG = DocumentViewerConfig()
    aria_label = "Document viewer"

    cfg = property(lambda self: self.config)

    def _render(self, *_, **__):
        url = self._abs(self.cfg.file_url)
        ext = (self.cfg.file_type or url.split("?")[0].split("#")[0]
                              .split(".")[-1]).lower()
        height = f"{self.cfg.height_rem}rem"

        # pdf
        if ext == "pdf":
            inner = (
                f'<iframe src="{url}" '
                f'style="width:100%;height:{height};border:none;"></iframe>'
            )

        # images
        elif ext in {"png", "jpg", "jpeg", "gif", "webp", "svg"}:
            inner = f'<img src="{url}" style="max-width:100%;height:auto;">'

        # rest
        else:
            fname = url.rsplit("/", 1)[-1]
            inner = (f'<a href="{url}" class="bfe-btn" download>'
                     f'📥 Download&nbsp;{fname}</a>')

        return mark_safe(f'<div id="{self.id}" class="bfe-card">{inner}</div>')

    def _abs(self, path: str) -> str:
        if path.startswith(("http://", "https://", "/")):
            return path
        return settings.MEDIA_URL.rstrip("/") + "/" + path.lstrip("/")

    def _compute_media(self) -> Media:
        return Media()


# todo: build registry?
