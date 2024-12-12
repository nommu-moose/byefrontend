from django.utils.safestring import mark_safe
from byefrontend.widgets import BFEBaseWidget
import json


class FileUploadWidget(BFEBaseWidget):
    aria_label = "File upload widget"
    inline_text = "Drop files here or click to upload."

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
        self.config = {
            'upload_url': config.get('upload_url', ''),
            'widget_html_id': config.get('widget_html_id', 'file_upload_widget'),
            'filetypes_accepted': config.get('filetypes_accepted', []),
            'auto_upload': config.get('auto_upload', True),
            'can_upload_multiple_files': config.get('can_upload_multiple_files', True),
            'fields': config.get('fields', [])
        }

        self.name = config.get('name', 'Untitled Upload Widget')

    def __str__(self):
        return self.render(self.name, False)

    def create_data_json(self):
        # Create a data JSON structure for the frontend.
        return {
            'upload_url': self.config['upload_url'],
            'widget_html_id': self.config['widget_html_id'],
            'filetypes_accepted': self.config['filetypes_accepted'],
            'auto_upload': self.config['auto_upload'],
            'can_upload_multiple_files': self.config['can_upload_multiple_files'],
            'fields': self.config['fields']
        }

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        if attrs is None:
            attrs = {}

        data_config = self.create_data_json()
        data_json = json.dumps(data_config)

        # Construct columns for fields: always have file_name, plus any additional fields
        fields = self.config['fields'] if not self.config['auto_upload'] else []
        # We'll always have a file_name column. Make sure it's visible:
        # Insert file_name at start if not present.
        has_file_name = any(f['field_name'] == 'file_name' for f in fields)
        if not has_file_name:
            fields.insert(0, {'field_name': 'file_name', 'editable': False, 'visible': True})
        # We'll have a thumbnail column as well. Prepend that:
        # Insert thumbnail column at start for display
        fields.insert(0, {'field_name': 'thumbnail', 'editable': False, 'visible': True})

        fields_html_headers = "".join(
            f"<th>{f['field_name']}</th>" for f in fields if f.get('visible', True)
        )

        # For "To Upload" and "Uploaded" lists, we show a table. If auto_upload=False,
        # "To Upload" table is editable. "Uploaded" table is read-only.
        upload_button_html = ""
        if not self.config['auto_upload']:
            upload_button_html = '<button type="button" id="upload-all-btn">Upload All</button>'

        file_upload_html = f'''
        <div id="{self.config['widget_html_id']}" class="file-upload-wrapper" 
             data-config='{data_json}'>

            <div id="drop-zone">{self.inline_text}</div>
            <input type="file" id="file-input" {'multiple' if self.config['can_upload_multiple_files'] else ''} style="display:none;"
            {'accept="' + ','.join(self.config['filetypes_accepted']) + '"' if self.config['filetypes_accepted'] else ''}>

            {upload_button_html}

            <div id="lists-container">
                <h3>To Upload</h3>
                <table id="to-upload-list" class="upload-table">
                    <thead>
                        <tr>
                            {fields_html_headers}
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>

                <h3>Uploaded</h3>
                <table id="uploaded-list" class="upload-table">
                    <thead>
                        <tr>
                            {fields_html_headers}
                            <th>Filepath</th>
                            <th>Actions</th>
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
