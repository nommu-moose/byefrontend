from __future__ import annotations

from dataclasses import replace

from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.hyperlink import HyperlinkConfig
from ..builders import ChildBuilderRegistry


class HyperlinkWidget(BFEBaseWidget):
    """
    Render a button-style hyperlink (<a …>) driven by `HyperlinkConfig`.

    * legacy uses such as `HyperlinkWidget(link='/foo', text='Foo')` still works
      because extra keyword arguments are merged into a private copy of the
      default config via :pyfunc:`dataclasses.replace` - try to stop this practice before removal
    """

    DEFAULT_CONFIG = HyperlinkConfig()

    def __init__(
        self,
        config: HyperlinkConfig | None = None,
        *,
        parent=None,
        **overrides,
    ):
        """
        Parameters

        config:
            A (possibly tweaked) `HyperlinkConfig` instance.
        overrides:
            Legacy keyword tweaks (`link=`, `text=`, `classes=` …)
            merged into *config* for painless migration.
        """
        if config is None:
            config = self.DEFAULT_CONFIG
        if overrides:
            config = replace(config, **overrides)

        super().__init__(config=config, parent=parent)

    cfg = property(lambda self: self.config)

    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        href = self._resolve_link()
        class_attr = " ".join(["btn", *self.cfg.classes])
        return mark_safe(
            f'<a id="{self.id}" href="{href}" class="{class_attr}">{self.cfg.text}</a>'
        )

    def _own_json(self):
        return {
            "uid": self.cfg.name,
            "text": self.cfg.text,
            "link": self._resolve_link(),
        }

    def _resolve_link(self) -> str:
        """
        Resolve cfg.link into a usable href:

        * absolute URL or path  -> used verbatim
        * Django view-name      -> reversed with *reverse_args*
        * anything else         -> returned untouched (best-effort)
        """
        link = self.cfg.link
        if link.startswith("/") or link.startswith("http"):
            return link

        try:
            return reverse(link, args=self.cfg.reverse_args)
        except NoReverseMatch:
            return link   # silently fall back – old behaviour

    class Media:
        css = {}
        js = {}


@ChildBuilderRegistry.register(HyperlinkConfig)
def _build_hyperlink(cfg: HyperlinkConfig, parent):
    from byefrontend.widgets.hyperlink import HyperlinkWidget
    return HyperlinkWidget(config=cfg, parent=parent)
