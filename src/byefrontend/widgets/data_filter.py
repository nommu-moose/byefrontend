from __future__ import annotations
import math, html
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from django.utils.safestring import mark_safe
from django.utils.http import urlencode

from ..configs.data_filter import DataFilterConfig
from ..configs.inline_form import InlineFormConfig
from ..configs.table       import TableConfig
from ..widgets.inline_form import InlineFormWidget
from ..widgets.table       import TableWidget
from ..widgets.base        import BFEBaseWidget
from ..builders            import ChildBuilderRegistry

class DataFilterWidget(BFEBaseWidget):
    """
    Combines an InlineFormWidget (filter controls) with
    a paginated, optionally-sorted TableWidget.
    """
    DEFAULT_CONFIG = DataFilterConfig()
    aria_label     = "Data table with filters & pagination"

    # shorthand
    cfg = property(lambda self: self.config)

    # ───────────────────────────────────────── construction
    def __init__(self,
                 *,
                 config: DataFilterConfig | None = None,
                 request=None,                       # pass-through for CSRF + GET params
                 parent: BFEBaseWidget | None = None,
                 **overrides):

        super().__init__(config=config, parent=parent, **overrides)

        # ---- 1. realise the inner filter-form ------------------------
        form_cfg = InlineFormConfig.build(
            action="",                      # current URL
            method="get",
            csrf=False,                     # GET → no CSRF
            gap=0.5,
            wrap=True,
            children=self.cfg.filters,
        )
        self._form = InlineFormWidget(config=form_cfg, parent=self,
                                      request=request)

        # ---- 2. slice + sort the dataset ----------------------------
        sliced = self._slice_and_sort(self.cfg.data)

        tbl_cfg = TableConfig(
            fields=self.cfg.table_fields,
            data=sliced,
        )
        self._table = TableWidget(config=tbl_cfg, parent=self)

        self._children = MappingProxyType({
            "form":  self._form,
            "table": self._table,
        })

    # ───────────────────────────────────────── helpers
    def _slice_and_sort(self, data: Sequence[Mapping[str, Any]]) -> Sequence[Mapping[str, Any]]:
        cfg = self.cfg
        # optional in-memory sort
        if cfg.sort_by:
            data = sorted(data,
                          key=lambda r: r.get(cfg.sort_by, ""),
                          reverse=(cfg.sort_dir == "desc"))
        # pagination
        psize  = min(cfg.page_size, cfg.max_page_size)
        start  = max(cfg.page - 1, 0) * psize
        return list(data)[start:start + psize]

    def _total_pages(self) -> int:
        return max(1, math.ceil(len(self.cfg.data) / max(1, self.cfg.page_size)))

    def _pagination_controls(self) -> str:
        page     = self.cfg.page
        last     = self._total_pages()
        if last == 1:
            return ""

        def _link(label, target, disabled=False):
            if disabled:
                return f'<span class="bfe-btn" style="opacity:.5;cursor:default;">{label}</span>'
            query = urlencode({"page": target})
            return f'<a href="?{html.escape(query)}" class="bfe-btn">{label}</a>'

        return (
            '<nav class="bfe-inline-group" style="gap:.5rem;justify-content:center;margin-top:var(--gap-md);">'
            f'{_link("« Prev", page - 1, page <= 1)}'
            f'<span>Page {page} / {last}</span>'
            f'{_link("Next »", page + 1, page >= last)}'
            '</nav>'
        )

    # ───────────────────────────────────────── rendering
    def _render(self, *_, **__) -> str:
        form_html  = self._form.render()
        table_html = self._table.render()
        pager_html = self._pagination_controls()

        return mark_safe(
            f'<section id="{self.id}" class="bfe-card">'
            f'{form_html}{table_html}{pager_html}'
            f'</section>'
        )

    # ───────────────────────────────────────── static media
    class Media:
        css = {}       # inherits button + card look from root.css
        js  = ()

# ——— register with the global builder ————————————
@ChildBuilderRegistry.register(DataFilterConfig)
def _build_datafilter(cfg: DataFilterConfig, parent):
    return DataFilterWidget(config=cfg, parent=parent)
