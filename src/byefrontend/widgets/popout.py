# src/byefrontend/widgets/popout.py
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..configs.popout import PopOutConfig
import uuid

class PopOut(BFEBaseWidget):
    DEFAULT_CONFIG = PopOutConfig()

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        cfg = self.config
        uid = uuid.uuid4().hex
        dialog_html = f"""
            <button data-popout-open="{uid}" class="bfe-btn">{cfg.trigger_text}</button>
            <dialog id="{uid}" class="bfe-popout" style="width:{cfg.width_px}px;height:{cfg.height_px}px;">
                <h3>{cfg.title}</h3>
                <button data-popout-close="{uid}" class="bfe-close">&times;</button>
                <div class="bfe-content">{value or ""}</div>
            </dialog>
        """
        return mark_safe(dialog_html)

    class Media:
        css = {"all": ("byefrontend/css/popout.css",)}
        js = ("byefrontend/js/popout.js",)
