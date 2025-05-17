# ── top-of-file imports ───────────────────────────────────────────────
from __future__ import annotations

from django.conf import settings
from django.forms.widgets import Media
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget                 # unchanged
from ..configs.document_viewer import DocumentViewerConfig
from ..builders import ChildBuilderRegistry


# ✂️ 1. Delete this line – we’re dropping pdf.js
# PDFJS_CDN = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build"


class DocumentViewerWidget(BFEBaseWidget):
    DEFAULT_CONFIG = DocumentViewerConfig()
    aria_label     = "Document viewer"

    cfg = property(lambda self: self.config)

    # ── rendering ─────────────────────────────────────────────────────
    def _render(self, *_, **__):
        url   = self._abs(self.cfg.file_url)
        ext   = (self.cfg.file_type or url.split("?")[0].split("#")[0]
                              .split(".")[-1]).lower()
        height = f"{self.cfg.height_rem}rem"

        # ---------- PDF ---------------------------------------------------
        if ext == "pdf":
            # 🆕 Simplified: native browser viewer inside an <iframe>
            inner = (
                f'<iframe src="{url}" '
                f'style="width:100%;height:{height};border:none;"></iframe>'
            )

        # ---------- Images ------------------------------------------------
        elif ext in {"png", "jpg", "jpeg", "gif", "webp", "svg"}:
            inner = f'<img src="{url}" style="max-width:100%;height:auto;">'

        # ---------- Everything else ---------------------------------------
        else:
            fname = url.rsplit("/", 1)[-1]
            inner = (f'<a href="{url}" class="bfe-btn" download>'
                     f'📥 Download&nbsp;{fname}</a>')

        return mark_safe(f'<div id="{self.id}" class="bfe-card">{inner}</div>')

    # ── helper (unchanged) ────────────────────────────────────────────
    def _abs(self, path: str) -> str:
        if path.startswith(("http://", "https://", "/")):
            return path
        return settings.MEDIA_URL.rstrip("/") + "/" + path.lstrip("/")

    # With pdf.js gone there are no external assets left.
    def _compute_media(self) -> Media:
        return Media()
