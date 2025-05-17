from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Sequence, Any

from .base import WidgetConfig
from .table import TableConfig                   # re-export convenience

@dataclass(frozen=True, slots=True)
class DataFilterConfig(WidgetConfig):
    """
    Immutable settings for DataFilterWidget.

    • filters        – mapping *name ➜ WidgetConfig* (rendered in an InlineForm)
    • data           – the **full, unfiltered** dataset: Sequence[Mapping]
    • table_fields   – TableWidget fields definition (same shape you already use)
    • page           – 1-based current page number
    • page_size      – rows per page
    • max_page_size  – hard cap (safety against “100 000 rows per page”)
    • sort_by / dir  – optional client-side sort when the dataset is a Python list
    """
    filters: Mapping[str, WidgetConfig]           = field(default_factory=dict)
    data:    Sequence[Mapping[str, Any]]          = field(default_factory=list)
    table_fields: Sequence[Mapping[str, Any]]     = field(default_factory=list)

    page: int        = 1
    page_size: int   = 25
    max_page_size: int = 200

    sort_by: str | None = None
    sort_dir: str       = "asc"      # or "desc"
