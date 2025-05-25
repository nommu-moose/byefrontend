from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import List, Dict, Any, Tuple


@dataclass(slots=True, frozen=True)
class WidgetConfig:
    """
    Configuration object shared by every widget.

    The class is "frozen" so one widget cannot accidentally mutate another’s defaults
    to tweak a field for a single instance use :pyfunc:`dataclasses.replace`.
    """

    # identity & display
    name: str = "widget"
    html_id: str | None = None
    classes: Tuple[str, ...] = tuple()

    # behaviour
    required: bool = False

    # text
    label: str | None = None  # todo: None currently still renders as string
    help_text: str | None = None

    # raw HTML attrs (use ONLY for “unknown” props)
    attrs: Dict[str, Any] = field(default_factory=dict)
    # todo: compound/additive attr function for adding to a known but unhandled attr

    # constructor to merge overrides without breaking immutability
    @classmethod
    def build(cls, **overrides: Any) -> "WidgetConfig":
        return replace(cls(), **overrides)
