from __future__ import annotations

from dataclasses import field, dataclass
from typing import Sequence, Mapping

from .base import WidgetConfig


@dataclass(slots=True, frozen=True)
class FileUploadConfig(WidgetConfig):
    """
    Immutable configuration for :class:`FileUploadWidget`.

    Tweak it via `dataclasses.replace` *or* the shortcut
    ::
        from byefrontend.configs import tweak, FileUploadConfig
        cfg = tweak(FileUploadConfig(), auto_upload=True)
    """

    # behaviour
    upload_url: str = ""
    widget_html_id: str | None = None
    filetypes_accepted: Sequence[str] = tuple()
    auto_upload: bool = False
    can_upload_multiple_files: bool = True
    inline_text: str = "Drop files here or click to upload."

    # metadata columns shown in the JS table
    # Each mapping follows the legacy shape:
    #   {"field_name": "..", "field_text": "..", "field_type": "..", "editable": bool, "visible": bool}
    fields: Sequence[Mapping[str, object]] = field(default_factory=list)
