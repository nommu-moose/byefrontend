import json
import uuid

from django.utils.safestring import mark_safe
from django.utils.html import escapejs

from .base import HyperlinkWidget, BFEBaseWidget


class MultiInlineForm(BFEBaseWidget):
    pass


import json
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget


class TableWidget(Widget):
    """
    A general-purpose table widget that can render tabular data based on a
    configuration of fields. It can be used independently or integrated into
    other widgets (like FileUploadWidget) by passing the appropriate fields and data.
    """
    template_name = None  # We will generate HTML in render()
    scrollable = True

    def __init__(self, fields=None, data=None, table_id="", table_class="bfe-table-widget", attrs=None, **kwargs):
        """
        :param fields: A list of field dicts, e.g.:
            [
                {'field_name': 'thumbnail', 'field_text': 'Thumbnail', 'field_type': 'img', 'editable': False, 'visible': True},
                {'field_name': 'file_name', 'field_text': 'File Name', 'field_type': 'text', 'editable': True, 'visible': True},
                ...
            ]
        :param data: A list of row dicts, where keys map to field_name. For example:
            [
              {
                'thumbnail': 'path/to/img.jpg',
                'file_name': 'example.png',
              },
              ...
            ]
            If you have nested/hierarchical data, you can store them as a 'children' key and recurse.
        :param table_id: An optional HTML id for the table (e.g. "to-upload-list")
        :param table_class: CSS class(es) for the table
        """
        super().__init__(attrs)
        if fields is None:
            fields = []
        if data is None:
            data = []
        self.fields = fields
        self.data = data
        self.table_id = table_id
        self.table_class = table_class
        self.attrs = attrs or {}

    def render(self, name, value, attrs=None, renderer=None):
        # Merge attributes
        final_attrs = self.build_attrs(self.attrs, attrs)
        table_html = self.render_table(self.data, self.fields, table_id=self.table_id, table_class=self.table_class,
                                       attrs=final_attrs)
        return mark_safe(table_html)

    def render_table(self, data, fields, table_id="", table_class="", attrs=None):
        """
        Render the entire table. This can be a recursive method if `data` contains nested rows.
        `data`: list of row dicts.
        `fields`: list of field dicts.
        """
        attrs_str = self.flatatt(attrs) if attrs else ""

        # Filter only visible fields
        visible_fields = [f for f in fields if f.get('visible', True)]

        thead = "<thead><tr>" + "".join(
            f"<th>{f.get('field_text', f['field_name'])}</th>" for f in visible_fields
        ) + "</tr></thead>"

        tbody = "<tbody>"
        for row in data:
            tbody += self.render_row(row, visible_fields)
            # If hierarchical data:
            # if 'children' in row and isinstance(row['children'], list):
            #     tbody += self.render_table(row['children'], fields)
        tbody += "</tbody>"

        scroll_class = " bfe-scrollable" if self.scrollable else ""
        table_html = f'<table id="{table_id}" class="{table_class}{scroll_class}" {attrs_str}>{thead}{tbody}</table>'
        return table_html

    def render_row(self, row_data, fields):
        """
        Render a single table row.
        `row_data`: dict with field_name: value pairs.
        `fields`: list of field dicts (only visible ones).
        """
        row_html = "<tr>"
        for field in fields:
            cell_html = self.render_cell(row_data, field)
            row_html += f"<td>{cell_html}</td>"
        row_html += "</tr>"
        return row_html

    def render_cell(self, row_data, field):
        """
        Render a single cell. Logic for field_type and editable fields goes here.
        """
        field_name = field['field_name']
        field_type = field.get('field_type', 'text')
        editable = field.get('editable', False)

        # Get value for this cell
        value = row_data.get(field_name, "")

        if field_type == 'img':
            # value should be a URL or something representing the image
            if value:
                return f'<img src="{value}" class="bfe-thumbnail" alt="thumbnail">'
            else:
                return '<span class="bfe-icon">📄</span>'
        elif field_type == 'text':
            if editable:
                # Render an input for editing
                return f'<input type="text" name="{field_name}" value="{value}" data-field="{field_name}">'
            else:
                return f'{value}'
        elif field_type == 'actions':
            # For actions, we can just return placeholders or buttons
            # Actual actions can be bound by JS or by passing callbacks in data.
            # Here we just return a placeholder:
            return '<button class="bfe-action-remove">Remove</button>'
        else:
            # Unrecognized field_type, return value as text
            return f'{value}'

    def flatatt(self, attrs):
        """
        Convert attributes dict to HTML attributes string.
        """
        return ' '.join(f'{key}="{value}"' for key, value in attrs.items())

    class Media:
        css = {
            'all': ('byefrontend/css/table_widget.css',)
        }
        js = ('byefrontend/js/table_widget.js',)


class NavBarWidget(BFEBaseWidget):
    # to be changed to have option of a utility class so that no instantiation is needed - optimisation for threads
    aria_label = "Navbar for the site."
    DEFAULT_NAME = 'navbar_widget'

    def __init__(self, config, parent=None, attrs=None, **kwargs):
        """
        Initializes the NavBarWidget widget.

        :param attrs: HTML attributes to customize the navbar (e.g., class, id).
        :param args: Additional positional arguments (not currently used).
        :param kwargs: Additional keyword arguments (reserved for future use or subclassing).
        """
        super().__init__(attrs, parent, name=config.get('name', self.DEFAULT_NAME), **kwargs)
        self.text = config.get('text', 'Untitled Site')
        self.title_button = config.get('title_button', False)
        self.link = config.get('link', None)

        # can omit top navbar's name as redundant, but it's inserted for simplicity of js handling.
        self.selected_path = config.get('selected_path', [])

        self.children = {}
        self._process_config_items(config)

        self.parent_navbar = parent

        attrs = attrs or {}

        existing_classes = attrs.get('class', '')
        updated_classes = f"{existing_classes} bfe-navbar".strip()

        attrs['class'] = updated_classes

        self.attrs = attrs

    def _process_config_items(self, config):
        children = config.get('children', {})
        for key, item in children.items():
            item_type = item.get('type', 'HyperlinkWidget')
            if item_type == 'NavBarWidget':
                navbar = NavBarWidget(config=item, parent=self)
                self.children[key] = navbar
            elif item_type == 'HyperlinkWidget':
                hyperlink = HyperlinkWidget(text=item.get('text', ''), link=item.get('link', '#'), parent=self)
                self.children[key] = hyperlink

    def __str__(self):
        return self.render()

    def create_data_json(self, selected_path=None, first_recur=True):
        """
        Generates a JSON structure representing the hierarchical data for this navbar and its children.

        :return: A dictionary with the navigation structure.
        """
        # Determine if this navbar is selected
        if first_recur:
            is_selected = True
            child_selected_path = selected_path
        else:
            is_selected = bool(selected_path) and self.name == selected_path[0]
            print(f"{self.name} selected: {is_selected}")
            child_selected_path = selected_path[1:] if is_selected else []

        # Build the list of children
        children_list = []
        for key, value in self.children.items():
            if isinstance(value, NavBarWidget):
                option = value.create_data_json(child_selected_path, first_recur=False)
            elif isinstance(value, HyperlinkWidget):
                child_is_selected = bool(child_selected_path) and key == child_selected_path[0]
                option = {
                    'text': value.text,
                    'link': value.link,
                    'selected': child_is_selected,
                    'uid': str(uuid.uuid4()),
                }
            else:
                option = {}
            children_list.append(option)

        # Build the navbar data including its children
        navbar_data = {
            'title_button': self.title_button,
            'link': self.link,
            'name': self.name,
            'text': self.text,
            'children': children_list,
            'uid': str(uuid.uuid4()),
            'selected': is_selected
        }

        return navbar_data

    def render(self, attrs=None, renderer=None, *args, **kwargs):
        """
        Renders the navbar as HTML, with config for further sub-navbars.

        :param attrs: Additional HTML attributes.
        :param renderer: The renderer to use.
        :return: Safe HTML string.
        """
        if attrs is None:
            attrs = {}

        buttons_html = ''
        for key, value in self.children.items():
            if isinstance(value, NavBarWidget):
                button_text = value.text
            elif isinstance(value, HyperlinkWidget):
                button_text = value.text
            else:
                button_text = 'Unknown'
            buttons_html += f'<button data-option="{key}">{button_text}</button>'

        data_list = self.create_data_json(self.selected_path)

        data_json_escaped = json.dumps(data_list, indent=4)
        navbar_html = \
            f'''
            <div class="navbar-wrapper">
                <nav class="navbar-container" data-nav-config='{data_json_escaped}'>
                </nav>
            </div>
            '''

        return mark_safe(navbar_html)

    class Media:
        css = {
            'all': ('byefrontend/css/navbar.css',)
        }
        js = ('byefrontend/js/navbar.js',)


class PopOut:
    def __init__(self):
        pass
