# ── src/byefrontend/configs/table.py ──────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class TableConfig(WidgetConfig):
    """
    Immutable configuration for `TableWidget`.

    A *row* is any mapping whose keys match the ``field_name`` values
    declared below.  All values are rendered verbatim – special behaviour
    (thumbnails, buttons, etc.) is decided purely by ``field_type``.
    """

    # ── behaviour ────────────────────────────────────────────────────────────
    scrollable: bool = True

    # ── structural ──────────────────────────────────────────────────────────
    table_id: str = ""
    table_class: str = "bfe-table-widget"

    # ── data & schema ───────────────────────────────────────────────────────
    fields: Sequence[Mapping[str, object]] = field(default_factory=list)
    data: Sequence[Mapping[str, object]] = field(default_factory=list)
