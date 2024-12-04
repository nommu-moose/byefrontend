import json
import uuid

from django.utils.safestring import mark_safe
from django.utils.html import escapejs

from .base import HyperlinkWidget, BFEBaseWidget


class Table:
    scrollable = True

    def __init__(self):
        pass


class NavBarWidget(BFEBaseWidget):
    # to be changed to have option of a utility class so that no instantiation is needed - optimisation for threads
    aria_label = "Navbar for the site."

    def __init__(self, config, parent=None, attrs=None, *args, **kwargs):
        """
        Initializes the NavBarWidget widget.

        :param attrs: HTML attributes to customize the navbar (e.g., class, id).
        :param args: Additional positional arguments (not currently used).
        :param kwargs: Additional keyword arguments (reserved for future use or subclassing).
        """
        self.name = config.get('title', 'Untitled Navbar')
        self.text = config.get('text', 'Untitled Site')

        self.children = {}
        self._process_config_items(config)

        self.parent_navbar = parent

        self.selected_path = config.get('selected_path', [])
        print('\n\n\n', self.selected_path)

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

    def create_data_json(self, selected_path=None):
        """
        Generates a JSON structure representing the hierarchical data for this navbar and its children.

        :return: A JSON string with the navigation structure.
        """
        data_list = []
        for key, value in self.children.items():
            is_selected = selected_path and key == selected_path[0]
            if isinstance(value, NavBarWidget):
                child_selected_path = selected_path[1:] if is_selected else []
                option = {
                    'name': value.name,
                    'text': value.text,
                    'children': value.create_data_json(child_selected_path),
                    'id': str(uuid.uuid4()),
                    'selected': is_selected
                }
            elif isinstance(value, HyperlinkWidget):
                option = {
                    'text': value.text,
                    'link': value.link,
                    'selected': is_selected
                }
            else:
                option = {}
            data_list.append(option)
        return data_list

    def render(self, attrs=None, renderer=None):
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
            <nav class="navbar-container" data-nav-config='{data_json_escaped}'>
            </nav>
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
