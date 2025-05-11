# ── src/byefrontend/widgets/containers.py  (replace the old TableWidget) ─────
from __future__ import annotations

import uuid
import json
from typing import Sequence, Mapping

from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..configs.table import TableConfig


class TableWidget(BFEBaseWidget, Widget):
    """
    Renders a (possibly scrollable) HTML table based entirely on a
    frozen :class:`TableConfig`.

    *Every* public attribute now comes from the immutable config.
    If you need a slight tweak, use::

        from byefrontend.configs import TableConfig, tweak
        my_cfg = tweak(TableConfig(), scrollable=False)

    and pass ``config=my_cfg``.
    """

    DEFAULT_CONFIG = TableConfig()

    # --------------------------------------------------------------------- #
    #  Construction
    # --------------------------------------------------------------------- #
    def __init__(self,
                 config: TableConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        super().__init__(config=config, parent=parent, **overrides)

    # Convenience alias
    cfg = property(lambda self: self.config)

    # --------------------------------------------------------------------- #
    #  Rendering
    # --------------------------------------------------------------------- #
    def _render(self, name=None, value=None, attrs=None, renderer=None, **kwargs):
        html = self._render_table(
            data=list(self.cfg.data),
            fields=[f for f in self.cfg.fields if f.get("visible", True)],
            table_id=self.cfg.table_id or self.id,
            table_class=self.cfg.table_class,
            scrollable=self.cfg.scrollable,
        )
        return mark_safe(html)

    # .............................................
    #  PRIVATE HELPERS
    # .............................................
    def _render_table(self,
                      *,
                      data: Sequence[Mapping[str, object]],
                      fields: Sequence[Mapping[str, object]],
                      table_id: str,
                      table_class: str,
                      scrollable: bool) -> str:

        thead = "<thead><tr>" + "".join(
            f"<th>{field.get('field_text', field['field_name'])}</th>"
            for field in fields
        ) + "</tr></thead>"

        tbody_rows = (
            self._render_row(row, fields) for row in data
        )
        tbody = "<tbody>" + "".join(tbody_rows) + "</tbody>"

        scroll_cls = " bfe-scrollable" if scrollable else ""
        attrs_str = f'id="{table_id}" class="{table_class}{scroll_cls}"'

        return f"<table {attrs_str}>{thead}{tbody}</table>"

    def _render_row(self,
                    row_data: Mapping[str, object],
                    fields: Sequence[Mapping[str, object]]) -> str:
        cells = (
            f"<td>{self._render_cell(row_data, field)}</td>" for field in fields
        )
        return "<tr>" + "".join(cells) + "</tr>"

    def _render_cell(self,
                     row_data: Mapping[str, object],
                     field: Mapping[str, object]) -> str:
        ftype = field.get("field_type", "text")
        fname = field["field_name"]
        editable = field.get("editable", False)
        value = row_data.get(fname, "")

        if ftype == "img":
            if value:
                return f'<img src="{value}" class="bfe-thumbnail" alt="thumbnail">'
            return '<span class="bfe-icon">📄</span>'

        if ftype == "actions":
            # Minimal placeholder – bind real behaviour via JS
            return '<button class="bfe-action-remove">Remove</button>'

        # --- plain / editable text ---------------------------------------
        if editable:
            return (
                f'<input type="text" name="{fname}" value="{value}" '
                f'data-field="{fname}">'
            )
        return str(value)

    # --------------------------------------------------------------------- #
    #  Static media declaration  (unchanged)
    # --------------------------------------------------------------------- #
    class Media:
        css = {"all": ("byefrontend/css/table_widget.css",)}
        js = ("byefrontend/js/table_widget.js",)
