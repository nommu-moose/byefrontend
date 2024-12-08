from django.utils.safestring import mark_safe

from byefrontend.widgets import BFEBaseWidget


class FileUploadWidget(BFEBaseWidget):
    # to be changed to have option of a utility class so that no instantiation is needed - optimisation for threads
    aria_label = "File upload widget"
    inline_text = "Drop files here or click to upload."

    def __init__(self, config=None, parent=None, attrs=None, *args, **kwargs):
        """
        Initializes the FileUploadWidget.

        :param attrs: HTML attributes to customize the navbar (e.g., class, id).
        :param args: Additional positional arguments (not currently used).
        :param kwargs: Additional keyword arguments (reserved for future use or subclassing).
        """
        if config is None:
            config = {}
        self.name = config.get('name', 'Untitled Navbar')
        self.text = config.get('text', 'Untitled Site')
        self.title_button = config.get('title_button', False)
        self.link = config.get('link', None)

        self.parent_navbar = parent

        attrs = attrs or {}

        existing_classes = attrs.get('class', '')
        updated_classes = f"{existing_classes} bfe-navbar".strip()

        attrs['class'] = updated_classes

        self.attrs = attrs

    def __str__(self):
        return self.render()

    def create_data_json(self, selected_path=None, first_recur=True):
        file_upload_data = {}

        return file_upload_data

    def render(self, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}

        data_list = self.create_data_json()

        # data_json_escaped = json.dumps(data_list, indent=4)
        # need to add data json
        file_upload_html = \
            f'''
            <div class="file-upload-wrapper">
                <div id="drop-zone">{self.inline_text}</div>
                <input type="file" id="file-input" multiple style="display:none;">
                <div id="upload-list"></div>
                <div id="messages"></div>
            </div>
            '''

        return mark_safe(file_upload_html)

    class Media:
        css = {
            'all': ('byefrontend/css/file_upload.css',)
        }
        js = ('byefrontend/js/file_upload.js',)
