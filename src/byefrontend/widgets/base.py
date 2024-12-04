import uuid

from django.forms.widgets import PasswordInput, Textarea, Media
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


class BFEBaseWidget:
    @property
    def media(self):
        return Media(css=self.Media.css, js=self.Media.js)

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


class HyperlinkWidget:
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

    def get_html(self, view_mode):
        if not [self.edit_visible, self.view_visible][view_mode]:
            return None
        classes = ' '.join(['btn'] + self.classes)
        text = self.text
        link = reverse(self.link, args=self.reverse_args)
        return mark_safe(f'<a href="{link}" class="{classes}">{text}</a>')
