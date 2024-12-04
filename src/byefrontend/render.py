from django.utils.html import format_html, format_html_join
from django.forms import ModelForm, Form
from django.shortcuts import render
from byefrontend.widgets.base import BFEBaseWidget


def aggregate_media(*widgets):
    """
    Todo: change how media is handled, maybe make more modular and/or put handling into classes themselves?
    Aggregates CSS and JS media from a list of forms and their widgets.

    Parameters:
    - forms: A list of form instances.

    Returns:
    - A tuple containing two strings: the first with <link> tags for CSS, the second with <script> tags for JS.
    """
    all_css = set()
    all_js = set()
    all_css.add('/static/byefrontend/css/root.css')

    for widget in widgets:
        media = widget.media
        for css in media._css.get('all', []):
            all_css.add(f"/static/{css}")
        for js in media._js:
            all_js.add(f"/static/{js}")

        if isinstance(widget, Form) or isinstance(widget, ModelForm):
            get_form_media(widget, all_css, all_js)

    css_links = format_html_join('\n', '<link href="{0}" media="all" as="style" rel="preload" onload="this.rel=\'stylesheet\'">',
                                 ((css,) for css in all_css))
    js_scripts = format_html_join('\n', '<script src="{0}"></script>', ((js,) for js in all_js))

    return css_links, js_scripts


def get_form_media(form, all_css, all_js):
    for field in form:
        widget_media = field.field.widget.media
        for css in widget_media._css.get('all', []):
            all_css.add(f"/static/{css}")
        for js in widget_media._js:
            all_js.add(f"/static/{js}")


def render_with_automatic_static(request, template_name, context: dict):
    """gets the css/js etc. to include in the template and renders the template."""
    if context is None:
        context = {}
    all_forms = []
    for item in context.values():
        if isinstance(item, ModelForm) or isinstance(item, Form) or isinstance(item, BFEBaseWidget):
            all_forms.append(item)
    all_css, all_js = aggregate_media(*all_forms)

    context['all_css'] = all_css
    context['all_js'] = all_js
    print(all_css, all_js)
    return render(request, template_name, context)
