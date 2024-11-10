from django.utils.html import format_html, format_html_join
from django.forms import ModelForm, Form
from django.shortcuts import render


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

    css_links = format_html_join('\n', '<link href="{0}" media="all" as="style" rel="preload" onload="this.rel=\'stylesheet\'">',
                                 ((css,) for css in all_css))
    js_scripts = format_html_join('\n', '<script src="{0}"></script>', ((js,) for js in all_js))

    return css_links, js_scripts


def render_with_automatic_static(request, template_name, context: dict):
    """gets the css/js etc. to include in the template and renders the template."""
    if context is None:
        context = {}
    all_forms = []
    for item in context.values():
        if isinstance(item, ModelForm) or isinstance(item, Form):
            all_forms.append(item)
    all_css, all_js = aggregate_media(*all_forms)

    context['all_css'] = all_css
    context['all_js'] = all_js
    print(all_css, all_js)
    return render(request, template_name, context)
