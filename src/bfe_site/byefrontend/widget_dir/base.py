import uuid

from django.forms.widgets import PasswordInput
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


def aggregate_media(*forms):
    """
    Aggregates CSS and JS media from a list of forms and their widgets.

    Parameters:
    - forms: A list of form instances.

    Returns:
    - A tuple containing two strings: the first with <link> tags for CSS, the second with <script> tags for JS.
    """
    all_css = set()
    all_js = set()

    for form in forms:
        media = form.media
        for css in media._css.get('all', []):
            all_css.add(f"/static/{css}")
        for js in media._js:
            all_js.add(f"/static/{js}")

        for field in form:
            widget_media = field.field.widget.media
            for css in widget_media._css.get('all', []):
                all_css.add(f"/static/{css}")
            for js in widget_media._js:
                all_js.add(f"/static/{js}")

    css_links = format_html_join('\n', '<link href="{0}" media="all" rel="stylesheet">',
                                 ((css,) for css in all_css))
    js_scripts = format_html_join('\n', '<script src="{0}"></script>', ((js,) for js in all_js))

    return css_links, js_scripts


class PasswordWithToggleWidget(PasswordInput):

    def __init__(self, attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = {}
        existing_classes = attrs.get('class', '')
        updated_classes = f"{existing_classes} secret-entry-field".strip()
        attrs['class'] = updated_classes
        super().__init__(attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        widget_id = uuid.uuid4().hex
        html_id = f'{name}_{widget_id}'
        attrs['id'] = html_id

        password_html = super().render(name, value, attrs, renderer)

        if value is not None:
            password_html = password_html[:-1] + f' value="{value}">'

        toggle_html = f'''
            <button class="btn btn-outline-secondary secret-entry-toggle" type="button" data-bs-toggle="password" data-target="#{html_id}" data-icon="#icon-{html_id}">
                <i class="bi bi-eye-slash" id="icon-{html_id}"></i>
            </button>
        '''

        full_html = f'''
            {password_html}
            {toggle_html}
        '''

        return mark_safe(full_html)

    class Media:
        css = {
            'all': ('css/secret_field.css',)
        }
        js = ('js/secret_field.js',)


class MangoHyperlinkWidget:
    def __init__(self, name: str, link: str, text: str, classes: list = None, reverse_args: list[str] = None,
                 edit_visible: bool = True, view_visible: bool = True):
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
