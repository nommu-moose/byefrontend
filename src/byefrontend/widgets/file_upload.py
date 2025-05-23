from __future__ import annotations

import json
from dataclasses import replace
from typing import Sequence, Mapping

from django.utils.safestring import mark_safe

from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs.file_upload import FileUploadConfig
from .table import TableWidget

# ── new for table-cards ──────────────────────────────────────────
from ..widgets.card import CardWidget
from ..configs.card  import CardConfig
from ..configs.table import TableConfig


# todo: should this also be a form widget?
class FileUploadWidget(BFEBaseWidget):
    """
    Drag-and-drop / click-to-upload widget driven entirely by an
    immutable :class:`FileUploadConfig`.

    All public attributes are now read-only views onto that config
    — just like the other modernised widgets.
    """

    DEFAULT_CONFIG = FileUploadConfig()

    # Static default for the *four* legacy columns.  Users may extend
    # or replace them by tweaking the config’s ``fields``.
    _DEFAULT_FIELDS: Sequence[Mapping[str, object]] = (
        {"field_name": "thumbnail",  "field_text": "Thumbnail",
         "field_type": "img",     "editable": False, "visible": True},
        {"field_name": "file_name",  "field_text": "Destination File Name",
         "field_type": "text",    "editable": True,  "visible": True},
        {"field_name": "file_path",  "field_text": "Source File Name",
         "field_type": "text",    "editable": True,  "visible": True},
        {"field_name": "actions",    "field_text": "Actions",
         "field_type": "actions", "editable": False, "visible": True},
    )

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self,
                 config: FileUploadConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        """
        ``overrides`` is kept for painless migration:

        >>> FileUploadWidget(upload_url="/api/upload/")      # old style
        """

        overrides.setdefault("required", False)

        # (1) build / merge config
        if config is None:
            config = self.DEFAULT_CONFIG
        if overrides:
            config = replace(config, **overrides)

        # (2) ensure default column set if caller supplied nothing
        if not config.fields:
            config = replace(config, fields=list(self._DEFAULT_FIELDS))

        super().__init__(config=config, parent=parent)

    # Convenience alias; short to type & keeps templates readable
    cfg = property(lambda self: self.config)

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self, *_, **__) -> str:        # signature kept loose
        data_json = json.dumps(self._create_data_json())

        # When *auto_upload* is False we expose the metadata-entry table
        # and an “Upload All” button; otherwise the JS handles everything.
        fields_for_table = [
            {**f, "editable": False} for f in self.cfg.fields
        ] if self.cfg.auto_upload else self.cfg.fields
        tables_html = self._render_tables(fields_for_table)

        upload_all_btn = (
            '<button type="button" id="upload-all-btn">Upload All</button>'
            if not self.cfg.auto_upload else ""
        )

        html = f"""
        <div id="{self.cfg.widget_html_id or self.id}"
             class="bfe-card file-upload-wrapper"
             data-config='{data_json}'>
          <div id="drop-zone">{self.cfg.inline_text}</div>
          <input type="file" id="file-input"
                 {'multiple' if self.cfg.can_upload_multiple_files else ''}
                 {'accept="' + ','.join(self.cfg.filetypes_accepted) + '"' if self.cfg.filetypes_accepted else ''}
                 style="display:none;">
          {upload_all_btn}
          {tables_html}
          <div id="messages"></div>
        </div>
        """
        return mark_safe(html)

    # .............................................
    #  Helpers
    # .............................................
    def _create_data_json(self) -> Mapping[str, object]:
        """Shape expected by `file_upload.js`."""
        return {
            "upload_url": self.cfg.upload_url,
            "widget_html_id": self.cfg.widget_html_id or self.id,
            "filetypes_accepted": list(self.cfg.filetypes_accepted),
            "auto_upload": self.cfg.auto_upload,
            "can_upload_multiple_files": self.cfg.can_upload_multiple_files,
            "fields": list(self.cfg.fields),
        }

    def _render_tables(self, fields: Sequence[Mapping[str, object]]) -> str:
        """
        Wrap each table in a `CardWidget`, giving it a neat heading and
        the standard .bfe-card aesthetics.
        """

        # ---- build the two TableConfig objects -----------------------
        to_upload_tbl_cfg = TableConfig(
            fields=fields,
            data=[],
            table_id="to-upload-list",
            table_class="upload-table",
        )

        uploaded_tbl_cfg = TableConfig(
            fields=fields,
            data=[],
            table_id="uploaded-list",
            table_class="upload-table",
        )

        # ---- wrap each table inside a CardWidget ---------------------
        to_upload_card = CardWidget(config=CardConfig(
            title="To Upload",
            children={"tbl": to_upload_tbl_cfg},
        ), parent=self)

        uploaded_card  = CardWidget(config=CardConfig(
            title="Uploaded",
            children={"tbl": uploaded_tbl_cfg},
        ), parent=self)

        # ---- emit the combined HTML ----------------------------------
        return (
            '<div id="lists-container">'
            f'{to_upload_card.render()}'
            f'{uploaded_card.render()}'
            '</div>'
        )

    # ------------------------------------------------------------------ #
    #  Static media – unchanged
    # ------------------------------------------------------------------ #
    class Media:
        css = {"all": ("byefrontend/css/file_upload.css",)}
        js = ("byefrontend/js/file_upload.js",)


@ChildBuilderRegistry.register(FileUploadConfig)
def _build_file_upload(cfg: FileUploadConfig, parent):
    return FileUploadWidget(config=cfg, parent=parent)
