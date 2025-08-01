from __future__ import annotations
import json
from dataclasses import replace
from typing import Sequence, Mapping
from django.utils.safestring import mark_safe
from .base import BFEBaseWidget
from ..builders import ChildBuilderRegistry
from ..configs.file_upload import FileUploadConfig
from ..widgets.card import CardWidget
from ..configs.card  import CardConfig
from ..configs.table import TableConfig
from ..widgets.label import LabelWidget
from ..configs.label import LabelConfig
from django.forms.widgets import Media


# todo: should this also be a form widget?
class FileUploadWidget(BFEBaseWidget):
    """
    drag-and-drop / click-to-upload widget
    """

    DEFAULT_CONFIG = FileUploadConfig()

    # static default for the four legacy columns.  Users may extend or replace by tweaking config fields
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

    def __init__(self,
                 config: FileUploadConfig | None = None,
                 *,
                 parent=None,
                 **overrides):
        """
        `overrides` is kept for painless migration from legacy:
        >>> FileUploadWidget(upload_url="/api/upload/")  # old style
        """

        overrides.setdefault("required", False)

        if config is None:
            config = self.DEFAULT_CONFIG
        if overrides:
            config = replace(config, **overrides)

        if not config.fields:
            config = replace(config, fields=list(self._DEFAULT_FIELDS))

        super().__init__(config=config, parent=parent)

    cfg = property(lambda self: self.config)

    def _render(self, name: str | None = None, value=None,
                attrs=None, renderer=None, **__):
        input_id = f"{self.id}_input"

        # single file - styled similarly to the multi-file variant but without JS
        if not self.cfg.can_upload_multiple_files:
            accept_attr = (
                f' accept="{",".join(self.cfg.filetypes_accepted)}"'
                if self.cfg.filetypes_accepted else ""
            )
            required_attr = " required" if self.cfg.required else ""
            input_html = (
                f'<div id="{self.cfg.widget_html_id or self.id}"'
                f' class="bfe-card file-upload-wrapper file-upload-single">'
                f'  <label id="drop-zone" for="{input_id}">{self.cfg.inline_text}</label>'
                f'  <input type="file" id="{input_id}"'
                f'         name="{name or self.id}"{accept_attr}{required_attr}>'
                f'  <div id="messages"></div>'
                f'</div>'
            )
        else:
            # multi file: full drag+drop widget with JS tables
            data_json = json.dumps(self._create_data_json())

            fields_for_tbl = (
                [{**f, "editable": False} for f in self.cfg.fields]
                if self.cfg.auto_upload else self.cfg.fields
            )
            tables_html = self._render_tables(fields_for_tbl)

            upload_all_btn = (
                '' if self.cfg.auto_upload else
                '<button type="button" id="upload-all-btn">Upload All</button>'
            )

            accept_attr = (
                f' accept="{",".join(self.cfg.filetypes_accepted)}"'
                if self.cfg.filetypes_accepted else ""
            )

            input_html = (
                f'<div id="{self.cfg.widget_html_id or self.id}"'
                f' class="bfe-card file-upload-wrapper"'
                f' data-config="{data_json}">'  # JSON passed to file_upload.js
                f'  <div id="drop-zone">{self.cfg.inline_text}</div>'
                f'  <input type="file" id="{input_id}" multiple{accept_attr}>'
                f'  {upload_all_btn}'
                f'  {tables_html}'
                f'  <div id="messages"></div>'
                f'</div>'
            )

        # render <label> unless the widget is embedded in a Django Form
        # InlineFormWidget sets ``is_in_form=True`` so the label appears
        # inline with the upload control without an extra wrapper.
        label_html = ""
        if self.cfg.label and not self.cfg.is_in_form:
            lbl_cfg = LabelConfig(text=self.cfg.label, html_for=input_id)
            label_html = LabelWidget(config=lbl_cfg, parent=self).render()

        wrapper_style = ''
        if self.cfg.is_in_form:
            wrapper_style = ' style="flex-basis:100%;max-width:100%;"'

        return mark_safe(
            f'<div class="text-input-wrapper"{wrapper_style}>{label_html}{input_html}</div>'
        )

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
        auto_upload = True  ➜  only the “Uploaded” table is rendered
        auto_upload = False ➜  keep both “To Upload” and “Uploaded”
        """
        parts: list[str] = []

        # show “To Upload” only when users can queue files first
        if not self.cfg.auto_upload:
            to_upload_tbl = TableConfig(
                fields=fields, data=[], table_id="to-upload-list",
                table_class="upload-table",
            )
            to_upload_card = CardWidget(config=CardConfig(
                title="To Upload", children={"tbl": to_upload_tbl},
            ), parent=self)
            parts.append(to_upload_card.render())

        uploaded_tbl = TableConfig(
            fields=fields, data=[], table_id="uploaded-list",
            table_class="upload-table",
        )
        uploaded_card = CardWidget(config=CardConfig(
            title="Uploaded", children={"tbl": uploaded_tbl},
        ), parent=self)
        parts.append(uploaded_card.render())

        return f'<div id="lists-container">{"".join(parts)}</div>'

    def _compute_media(self) -> Media:
        """
        Skip the heavy JS bundle for the simple single-file variant.
        """
        css_files = ("byefrontend/css/file_upload.css",)
        if self.cfg.can_upload_multiple_files:
            return Media(css={"all": css_files},
                         js=("byefrontend/js/file_upload.js",))
        return Media(css={"all": css_files}, js=())


@ChildBuilderRegistry.register(FileUploadConfig)
def _build_file_upload(cfg: FileUploadConfig, parent):
    return FileUploadWidget(config=cfg, parent=parent)
