from django.forms import Form, ModelForm
from django.utils.html import format_html_join
from django.shortcuts import render
from django.forms.widgets import Media
from collections.abc import Iterable

def collect_media(component, all_css, all_js):
    """
    Recursively collects media assets from a component and its children.

    Parameters:
    - component: The component to collect media from.
    - all_css: A set to collect CSS files.
    - all_js: A set to collect JS files.
    """
    # Get media from the component
    if hasattr(component, 'media'):
        media = component.media
        for css in media._css.get('all', []):
            all_css.add(f"/static/{css}")
        for js in media._js:
            all_js.add(f"/static/{js}")

    # If component is a form, get media from its fields
    if isinstance(component, (Form, ModelForm)):
        for field in component:
            collect_media(field.field.widget, all_css, all_js)

    # If component has children, recursively get their media
    if hasattr(component, 'children') and isinstance(component.children, dict):
        for child in component.children.values():
            collect_media(child, all_css, all_js)
    # If component has a list of widgets (for cases like formsets)
    elif hasattr(component, 'widgets') and isinstance(component.widgets, Iterable):
        for widget in component.widgets:
            collect_media(widget, all_css, all_js)
    # Custom logic for components with other nested elements
    elif hasattr(component, 'get_nested_components'):
        for nested_component in component.get_nested_components():
            collect_media(nested_component, all_css, all_js)

def aggregate_media(*components):
    """
    Aggregates CSS and JS media from a list of components (forms, widgets, etc.).

    Parameters:
    - components: A list of components.

    Returns:
    - A tuple containing two strings: the first with <link> tags for CSS, the second with <script> tags for JS.
    """
    all_css = set()
    all_js = set()
    all_css.add('/static/byefrontend/css/root.css')

    for component in components:
        collect_media(component, all_css, all_js)

    css_links = format_html_join(
        '\n',
        '<link href="{0}" media="all" as="style" rel="preload" onload="this.rel=\'stylesheet\'">',
        ((css,) for css in all_css)
    )
    js_scripts = format_html_join(
        '\n',
        '<script src="{0}"></script>',
        ((js,) for js in all_js)
    )

    return css_links, js_scripts

def render_with_automatic_static(request, template_name, context=None):
    """
    Renders the template with automatic inclusion of CSS and JS media assets.

    Parameters:
    - request: The HTTP request object.
    - template_name: The name of the template to render.
    - context: The context dictionary for the template.

    Returns:
    - An HttpResponse object with the rendered template.
    """
    if context is None:
        context = {}
    all_components = []
    for item in context.values():
        if hasattr(item, 'media') or hasattr(item, 'children') or isinstance(item, (Form, ModelForm)):
            all_components.append(item)
    all_css, all_js = aggregate_media(*all_components)

    context['all_css'] = all_css
    context['all_js'] = all_js
    return render(request, template_name, context)
