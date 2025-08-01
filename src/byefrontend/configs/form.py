from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping
from .base import WidgetConfig


@dataclass(frozen=True, slots=True)
class FormConfig(WidgetConfig):
    """
    Immutable settings for BFEFormWidget.

    - action        – <form action="…">
    - method        – "post" by default
    - csrf          – inject csrf automatically
    - multipart     – force enctype="multipart/form-data"
                      (auto-enabled when any FileUploadWidget detected)
    - prefix        – optional form-prefix (same semantics as Django’s)
    - children      – mapping name -> WidgetConfig
    """
    action: str = ""
    method: str = "post"
    csrf: bool = True
    multipart: bool = False
    prefix: str | None = None
    submit_text: str = "Submit"
    children: Mapping[str, WidgetConfig] = field(default_factory=dict)
