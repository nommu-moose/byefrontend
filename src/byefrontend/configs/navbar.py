# ── src/byefrontend/configs/navbar.py ────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .base import WidgetConfig
from .hyperlink import HyperlinkConfig   # forward reference for type hints


@dataclass(frozen=True, slots=True)
class NavBarConfig(WidgetConfig):
    """
    Immutable configuration used by :class:`NavBarWidget`.

    * Every field has a safe default so callers can always write
      `NavBarConfig()` and tweak selected bits with
      `dataclasses.replace`/`byefrontend.configs.tweak`.
    """
    text: str = "Untitled Site"
    title_button: bool = False
    link: str | None = None

    # ── selection / focus ───────────────────────────────────────────────────────
    selected_path: Sequence[str] = tuple()

    # ── hierarchical children ──────────────────────────────────────────────────
    # The mapping can mix NavBarConfig and HyperlinkConfig objects.
    children: Mapping[str, "NavBarConfig | HyperlinkConfig"] = field(default_factory=dict)
