import uuid

from django.forms.widgets import PasswordInput, Textarea, Media
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


class BFEChildrenDict(dict):
    # in future make it force all instances to only have one dictionary they're part of?
    # # # this would need a parent_dict attr too.
    # auto set parents of sub objects?
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.mark_parent_for_recache()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        # If adding or replacing a child widget, ensure it knows about its parent
        if hasattr(value, 'parent'):
            value.parent = self.parent
        super().__setitem__(key, value)
        # Since we've changed the structure of children, mark parent as needing recache
        self.mark_parent_for_recache()

    def __delitem__(self, key):
        super().__delitem__(key)
        # Removing a child also affects rendering
        self.mark_parent_for_recache()

    def clear(self):
        super().clear()
        self.mark_parent_for_recache()

    def pop(self, key, default=None):
        val = super().pop(key, default)
        self.mark_parent_for_recache()
        return val

    def popitem(self):
        val = super().popitem()
        self.mark_parent_for_recache()
        return val

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        # On updating multiple items, also ensure recache
        self.mark_parent_for_recache()

    def mark_parent_for_recache(self):
        self.parent.needs_render_recache = True
        self.parent._needs_media_recache = True


class BFEBaseWidget:
    # if render is passed attrs, don't use cache at all - assume unique
    DEFAULT_CACHE_RELEVANT_ATTRS = {
        'name', 'id', 'classes', 'attrs', 'value', 'label', 'help_text',
        'required', 'widget_type', 'children', 'aria_label'
    }
    cache_relevant_attrs = DEFAULT_CACHE_RELEVANT_ATTRS

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'widget')
        self.id = kwargs.get('id', self.generate_id())
        self.classes = kwargs.get('classes', [])
        self.attrs = kwargs.get('attrs', {})
        self.value = kwargs.get('value')
        self.label = kwargs.get('label', None)
        self.help_text = kwargs.get('help_text', None)
        self.required = kwargs.get('required', False)
        self.widget_type = kwargs.get('widget_type', 'text')
        self.parent = kwargs.pop('parent', None)
        self._needs_render_recache = True
        self.cached_render = ''
        self.cached_media = None
        self._needs_media_recache = True
        self._children = BFEChildrenDict(self)

    def generate_id(self):
        return f"{self.name}_{str(uuid.uuid4())}"

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError('children must be a dict')
        self._children.clear()
        self._children.update(value)

    def __setattr__(self, name, value):
        if name in self.cache_relevant_attrs:
            self._needs_render_recache = True
        super().__setattr__(name, value)

    @property
    def needs_render_recache(self):
        return self._needs_render_recache

    @needs_render_recache.setter
    def needs_render_recache(self, value: bool):
        if value:
            self._needs_render_recache = True
            if self.parent is not None:
                self.parent.needs_render_recache = True

    def render(self, *args, **kwargs):
        if self.needs_render_recache:
            self.cached_render = self._render(args, kwargs)
        return self.cached_render

    def _render(self, *args, **kwargs):
        return self.cached_render

    @property
    def media(self):
        """
        Returns a Media object that aggregates both this widget's media and its children's media.
        If the media needs recaching, it will be recomputed.
        """
        if self._needs_media_recache:
            self.cached_media = self._compute_media()
            self._needs_media_recache = False
        return self.cached_media

    def _compute_media(self):
        """
        Compute the merged Media for this widget and all of its children.
        """
        own_media = Media(css=self.Media.css, js=self.Media.js)
        child_medias = [child.media for child in self.children.values() if hasattr(child, 'media')]
        # Merge all children's media into own_media
        for cm in child_medias:
            own_media += cm
        return own_media

    class Media:
        css = {}
        js = ()


class CodeBoxWidget(Textarea):
    pass


class SecretToggleCharWidget(PasswordInput):
    aria_label = "Toggle Secret Field Visibility"

    def __init__(self, attrs=None, input_type='password', *args, **kwargs):
        """
        Initializes the widget.

        :param attrs: HTML attributes for the widget.
        :param input_type: The type of the input (default is 'password').
        """
        if attrs is None:
            attrs = {}
        existing_classes = attrs.get('class', '')
        updated_classes = f"{existing_classes} secret-entry-field".strip()
        attrs['class'] = updated_classes
        self.input_type = input_type
        super().__init__(attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renders the widget as HTML with a toggle button.

        :param name: The name of the input.
        :param value: The value of the input.
        :param attrs: Additional HTML attributes.
        :param renderer: The renderer to use.
        :return: Safe HTML string.
        """
        if attrs is None:
            attrs = {}
        # Generate a unique ID for the widget instance
        unique_id = uuid.uuid4().hex
        html_id = attrs.get('id', f'id_{name}_{unique_id}')
        attrs['id'] = html_id
        attrs['type'] = self.input_type

        # Render the input field
        input_html = super().render(name, value, attrs, renderer)

        # Ensure the value is correctly set
        if value is not None:
            input_html = input_html[:-1] + f' value="{value}">'

        # Render the toggle button with unique data attributes
        toggle_html = \
            f'''
            <button class="secret-entry-toggle" type="button" 
                    data-bs-toggle="password" 
                    data-target="#{html_id}" 
                    data-icon="#icon-{unique_id}"
                    aria-label="{self.aria_label}">
                <i class="eye-icon eye-closed" id="icon-{unique_id}"></i>
            </button>
            '''

        # Combine input and toggle button
        full_html = f'''
            <div class="secret-input-wrapper" style="position: relative;">
                {input_html}
                {toggle_html}
            </div>
        '''

        return mark_safe(full_html)

    class Media:
        css = {
            'all': ('byefrontend/css/secret_field.css',)
        }
        js = ('byefrontend/js/secret_field.js',)


class HyperlinkWidget(BFEBaseWidget):
    def __init__(self, link: str, text: str, classes: list = None, reverse_args: list[str] = None,
                 edit_visible: bool = True, view_visible: bool = True, parent=None):
        self.parent = parent
        self.link = link
        self.text = text
        if classes is None:
            classes = ['btn-success']
        self.classes = classes
        if type(reverse_args) is str:
            reverse_args = [reverse_args]
        elif reverse_args is None:
            reverse_args = []
        self.reverse_args = reverse_args
        self.edit_visible = edit_visible
        self.view_visible = view_visible

    def __str__(self):
        return self.render()

    def render(self, attrs=None, renderer=None, *args, **kwargs):  # old: (self, name, value, attrs=None, renderer=None)
        """
        Renders the widget as HTML with a toggle button.

        :param name: The name of the input.
        :param value: The value of the input.
        :param attrs: Additional HTML attributes.
        :param renderer: The renderer to use.
        :return: Safe HTML string.
        """
        if attrs is None:
            attrs = {}
        # Generate a unique ID for the widget instance
        unique_id = uuid.uuid4().hex
        html_id = attrs.get('id', f'id_{name}_{unique_id}')
        attrs['id'] = html_id

        classes = ' '.join(['btn'] + self.classes)
        text = self.text
        link = reverse(self.link, args=self.reverse_args)
        return mark_safe(f'<a href="{link}" class="{classes}">{text}</a>')


class TinyThumbnailWidget:
    pass


class TitleWidget:
    pass


class InputFieldWidget:
    pass


class BoxInputWidget:
    pass


class TextInputWidget:
    pass


class LabelWidget:
    pass


class CheckBoxWidget:
    pass


class RadioWidget:
    pass
