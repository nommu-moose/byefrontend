import json
import uuid

from django.utils.safestring import mark_safe
from django.utils.html import escapejs

from .base import HyperlinkWidget, BFEBaseWidget


class MultiInlineForm(BFEBaseWidget):
    pass


class TableWidget(BFEBaseWidget):
    scrollable = True

    def __init__(self):
        pass


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
