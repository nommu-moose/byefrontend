# ── src/byefrontend/widgets/document_viewer.py ──────────────────────
"""
DocumentViewerWidget – multi-page, scrollable PDF viewer.

Key features
------------
• Renders **all pages** into <canvas> elements, appended one-after-another,
  giving you natural scrolling inside the pop-out (or anywhere else).
• Uses jsDelivr for pdf.js + worker → zero extra static setup.
• Graceful fallback to a plain <iframe> when the CDN is unreachable.
"""

from __future__ import annotations

from django.conf import settings
from django.forms.widgets import Media
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.document_viewer import DocumentViewerConfig
from ..builders import ChildBuilderRegistry

PDFJS_CDN = "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build"


class DocumentViewerWidget(BFEBaseWidget):
    DEFAULT_CONFIG = DocumentViewerConfig()
    aria_label = "Document viewer"

    cfg = property(lambda self: self.config)

    # ─────────────────────────────────────────────────────────── render
    def _render(self, *_, **__):
        url = self._abs(self.cfg.file_url)
        ext = (self.cfg.file_type or url.split("?")[0].split("#")[0]
               .split(".")[-1]).lower()
        height = f"{self.cfg.height_rem}rem"

        # ---------- PDF -------------------------------------------------
        if ext == "pdf":
            viewer_id = f"{self.id}_viewer"
            pdf_js = f"{PDFJS_CDN}/pdf.min.js"
            worker_js = f"{PDFJS_CDN}/pdf.worker.min.js"

            inner = f"""
              <div id="{viewer_id}"
                   style="height:{height};overflow:auto;background:#f8f8f8;"></div>

              <script src="{pdf_js}"></script>
              <script>
                (function() {{
                  const url      = "{url}";
                  const viewer   = document.getElementById("{viewer_id}");

                  /* Native-viewer fallback */
                  function fallback() {{
                    viewer.innerHTML =
                      '<iframe src="' + url + '" ' +
                      'style="width:100%;height:100%;border:none"></iframe>';
                  }}

                  /* pdf.js missing? ➜ fallback immediately */
                  if (typeof pdfjsLib === "undefined") {{ fallback(); return; }}

                  pdfjsLib.GlobalWorkerOptions.workerSrc = "{worker_js}";

                  pdfjsLib.getDocument(url).promise.then(pdf => {{
                    const total = pdf.numPages;
                    const desiredWidth = viewer.clientWidth || 600;

                    /* Render every page */
                    for (let n = 1; n <= total; n++) {{
                      pdf.getPage(n).then(page => {{
                        const vp1    = page.getViewport({{ scale: 1 }});
                        const scale  = desiredWidth / vp1.width;
                        const vp     = page.getViewport({{ scale }});

                        const canvas = document.createElement('canvas');
                        canvas.width  = vp.width;
                        canvas.height = vp.height;
                        viewer.appendChild(canvas);

                        page.render({{
                          canvasContext: canvas.getContext('2d'),
                          viewport:      vp
                        }});
                      }});
                    }}
                  }}).catch(err => {{
                    console.error("pdf.js failure – using <iframe> fallback", err);
                    fallback();
                  }});
                }})();
              </script>
            """

        # ---------- Images ---------------------------------------------
        elif ext in {"png", "jpg", "jpeg", "gif", "webp", "svg"}:
            inner = f'<img src="{url}" style="max-width:100%;height:auto;">'

        # ---------- Other files ----------------------------------------
        else:
            fname = url.rsplit("/", 1)[-1]
            inner = (f'<a href="{url}" class="bfe-btn" download>'
                     f'📥 Download&nbsp;{fname}</a>')

        return mark_safe(f'<div id="{self.id}" class="bfe-card">{inner}</div>')

    # ───────────────────────────────────────────────────────── utilities
    def _abs(self, path: str) -> str:
        if path.startswith(("http://", "https://", "/")):
            return path
        return settings.MEDIA_URL.rstrip("/") + "/" + path.lstrip("/")

    # No local static assets required – everything comes from the CDN
    def _compute_media(self) -> Media:
        return Media()


@ChildBuilderRegistry.register(DocumentViewerConfig)
def _build_docviewer(cfg: DocumentViewerConfig, parent):
    return DocumentViewerWidget(config=cfg, parent=parent)
