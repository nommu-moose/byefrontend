from django.utils.safestring import mark_safe
from byefrontend.widgets import BFEBaseWidget
import json


class FileUploadWidget(BFEBaseWidget):
    aria_label = "File upload widget"
    inline_text = "Drop files here or click to upload."
    fields = [
        {'field_name': 'thumbnail', 'field_text': 'Thumbnail', 'field_type': 'img', 'editable': False, 'visible': True},
        {'field_name': 'file_name', 'field_text': 'Destination File Name', 'field_type': 'text', 'editable': True, 'visible': True},
        {'field_name': 'file_path', 'field_text': 'Source File Name', 'field_type': 'text', 'editable': True, 'visible': True},
        {'field_name': 'actions', 'field_text': 'Actions', 'field_type': 'actions', 'editable': False, 'visible': True}
    ]

    def __init__(self, config=None, attrs=None, parent=None, **kwargs):
        """
        Initializes the FileUploadWidget with extended config.

        Expected config keys:
        - upload_url: str, URL to submit files to
        - widget_html_id: str, unique HTML ID for this widget
        - filetypes_accepted: list of MIME strings, e.g. ['image/png','image/jpeg']
        - auto_upload: bool, if True files upload immediately
        - can_upload_multiple_files: bool, if True multiple files can be added
        - fields: list of dict for metadata fields if auto_upload=False
                  Each field: {"field_name": "title", "editable": true, "visible": true}
                  'file_name' is a default field always included.

        :param config: configuration dictionary
        :param parent: parent widget (if any)
        :param attrs: HTML attributes
        """
        super().__init__(attrs=attrs, parent=parent, **kwargs)
        if config is None:
            config = {}
        self.name = config.get('name', 'Untitled Upload Widget')
        self.upload_url = config.get('upload_url', '')
        self.widget_html_id = config.get('widget_html_id', self.generate_id())
        self.filetypes_accepted = config.get('filetypes_accepted', [])
        self.auto_upload = config.get('auto_upload', False)
        self.can_upload_multiple_files = config.get('can_upload_multiple_files', True)
        self.fields = self.__class__.fields[:-1] + config.get('fields', []) + [self.__class__.fields[-1]]

    def __str__(self):
        return self.render(self.name, False)

    def create_data_json(self):
        # Create a data JSON structure for the frontend.
        return {
            'upload_url': self.upload_url,
            'widget_html_id': self.widget_html_id,
            'filetypes_accepted': self.filetypes_accepted,
            'auto_upload': self.auto_upload,
            'can_upload_multiple_files': self.can_upload_multiple_files,
            'fields': self.fields,
        }

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        if attrs is None:
            attrs = {}

        data_config = self.create_data_json()
        data_json = json.dumps(data_config)

        # Construct columns for fields: always have file_name, plus any additional fields
        fields = self.fields if not self.auto_upload else []

        fields_html_headers = "".join(
            f"<th>{f['field_name']}</th>" for f in fields if f.get('visible', True)
        )

        # For "To Upload" and "Uploaded" lists, we show a table. If auto_upload=False,
        # "To Upload" table is editable. "Uploaded" table is read-only.
        upload_button_html = ""
        if not self.auto_upload:
            upload_button_html = '<button type="button" id="upload-all-btn">Upload All</button>'
        print(data_json)

        fields_html_headers = "".join(
            f"<th>{f.get('field_text', f['field_name'])}</th>"
            for f in fields if f.get('visible', True)
        )

        file_upload_html = f'''
        <div id="{self.widget_html_id}" class="file-upload-wrapper" 
             data-config='{data_json}'>

            <div id="drop-zone">{self.inline_text}</div>
            <input type="file" id="file-input" {'multiple' if self.can_upload_multiple_files else ''} 
            {'accept="' + ','.join(self.filetypes_accepted) + '"' if self.filetypes_accepted else ''} style="display:none;">

            {upload_button_html}

            <div id="lists-container">
                <h3>To Upload</h3>
                <table id="to-upload-list" class="upload-table">
                    <thead>
                        <tr>
                            {fields_html_headers}
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>

                <h3>Uploaded</h3>
                <table id="uploaded-list" class="upload-table">
                    <thead>
                        <tr>
                            {fields_html_headers}
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>

            <div id="messages"></div>
        </div>
        '''

        return mark_safe(file_upload_html)

    class Media:
        css = {
            'all': ('byefrontend/css/file_upload.css',)
        }
        js = ('byefrontend/js/file_upload.js',)
