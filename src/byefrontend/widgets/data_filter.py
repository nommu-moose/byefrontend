from __future__ import annotations
import math, html
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from django.utils.safestring import mark_safe
from django.http import QueryDict

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

        # store the original query-string so we can preserve it later
        self._query_dict = request.GET.copy() if request is not None else QueryDict('', mutable=True)

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

    # ───────────────────────────────────────── pagination controls
    # ───────────────────────────────────────── pagination controls
    def _pagination_controls(self) -> str:
        """
        Pager with:
        • « First / « Prev / Next » / Last » buttons
        • an <input type="number"> to jump directly to any page
        • tiny inline JS to keep all other query-string parameters
          intact when navigating.
        """
        page = self.cfg.page
        last = self._total_pages()
        if last == 1:                         # nothing to paginate
            return ""

        # helper to emit either <a …> or a disabled <span …>
        def _link(label: str, target: int, disabled: bool = False) -> str:
            if disabled:
                return (
                    '<span class="bfe-btn" '
                    'style="opacity:.5;cursor:default;">'
                    f'{label}</span>'
                )

            # 2 ️⃣  merge *all* current GET params with the new page number
            query_dict = self._query_dict.copy()
            query_dict['page'] = str(target)
            query = query_dict.urlencode()

            return f'<a href="?{html.escape(query)}" class="bfe-btn">{label}</a>'

        pager_id = f"{self.id}_pager"         # unique per widget

        # final HTML ----------------------------------------------------
        return (
            f'<nav id="{pager_id}" class="bfe-inline-group pagination" '
            f'style="gap:.5rem;justify-content:center;margin-top:var(--gap-md);">'
            f'{_link("« First", 1, page == 1)}'
            f'{_link("« Prev",  page - 1, page == 1)}'

            # numeric jump-field
            f'<span>Page</span>'
            f'<input type="number" id="{pager_id}_input" value="{page}" '
            f'min="1" max="{last}" style="width:4rem;text-align:center;">'
            f'<span>/ {last}</span>'
            f'<button type="button" class="bfe-btn" id="{pager_id}_go">Go</button>'

            f'{_link("Next »", page + 1, page == last)}'
            f'{_link("Last »", last, page == last)}'
            f'</nav>'

            # JS: change only the page= parameter, keep filters & sorts
            f'<script>(function(){{'
            f' const go  = document.getElementById("{pager_id}_go");'
            f' const inp = document.getElementById("{pager_id}_input");'
            f' if(!go||!inp) return;'
            f' const jump = () => {{'
            f'   const n = parseInt(inp.value,10);'
            f'   if(!n||n<1||n>{last}) return;'
            f'   const url = new URL(window.location);'
            f'   url.searchParams.set("page", n);'
            f'   window.location.href = url;'
            f' }};'
            f' go.addEventListener("click", jump);'
            f' inp.addEventListener("keydown", e=>{{if(e.key==="Enter"){{e.preventDefault();jump();}}}});'
            f'}})();</script>'
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
