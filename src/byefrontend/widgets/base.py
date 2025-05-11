import uuid

from django.forms.widgets import PasswordInput, Textarea, Media, Widget
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import format_html, format_html_join
from django.conf import settings
from dataclasses import replace
from byefrontend.configs.base import WidgetConfig


class BFEChildrenDict(dict):
    # in future make it force all instances to only have one dictionary they're part of?
    # # # this would need a parent_dict attr too.
    # auto set parents of sub objects?
    def __init__(self, parent, parent_recache_type=None, **kwargs):
        if parent_recache_type not in ['media', 'render', None]:
            raise Exception("Invalid parent_recache_type")
        if parent_recache_type is None:
            parent_recache_type = ['_needs_media_recache', 'needs_render_recache']
        else:
            parent_recache_type = [
                {'media': '_needs_media_recache', 'render': 'needs_render_recache'}[parent_recache_type]
            ]
        self.parent_recache_type = parent_recache_type
        self.parent = parent
        self.mark_parent_for_recache()
        super().__init__(**kwargs)

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
        for key in self.parent_recache_type:
            setattr(self.parent, key, True)


class BFEBaseWidget:
    """
    Base class for all ByeFrontend widgets.

    NOTE:
      *Every* concrete widget will eventually delegate its public
      properties to the immutable :class:`WidgetConfig`.  For now we
      map the most common fields so existing templates keep working.
    """
    DEFAULT_CONFIG = WidgetConfig()
    # if render is passed attrs, don't use cache at all - assume unique
    DEFAULT_CACHE_RELEVANT_ATTRS = {
        'name', 'id', 'classes', 'attrs', 'value', 'label', 'help_text',
        'required', 'widget_type', 'children', 'aria_label'
    }
    cache_relevant_attrs = DEFAULT_CACHE_RELEVANT_ATTRS
    DEFAULT_NAME = 'widget'
    classes = []

    def __init__(
        self,
        config: WidgetConfig | None = None,
        *,
        parent=None,
        **overrides,               # ← legacy keyword support
    ):
        # ----------------------------------------------------------------------------
        # 1.  Build a *dedicated* config instance for *this* widget
        # ----------------------------------------------------------------------------
        if config is None:
            config = self.__class__.DEFAULT_CONFIG
        # Merge in legacy keyword overrides (label=…, required=… etc.).
        if overrides:
            config = replace(config, **overrides)
        self.config: WidgetConfig = config  # 💡 keep it public but immutable

        # ----------------------------------------------------------------------------
        # 2.  Expose the *historical* attributes so existing code does not break.
        #    Every attribute is read from the config – never written back.
        # ----------------------------------------------------------------------------
        self.parent = parent
        self.name = self.config.name
        self.id = self.config.html_id or self.generate_id()
        self.label = self.config.label
        self.help_text = self.config.help_text
        self.required = self.config.required
        # keep a *private* mutable copy of attrs for this instance
        self._attrs = BFEChildrenDict(parent=self, parent_recache_type="render")
        self._attrs.update({**self.config.attrs})  # shallow copy is fine – values are primitives

        # ----------------------------------------------------------------------------
        # 3.  Cache bookkeeping remains exactly as before
        # ----------------------------------------------------------------------------
        self._needs_render_recache = True
        self.cached_render = ""
        self.cached_media = None
        self._needs_media_recache = True
        self._children = BFEChildrenDict(parent=self)

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value: dict):
        if not isinstance(value, dict):
            txt = f"attrs must be a dict, you're passing a {type(value)}"
            raise TypeError(txt)
        self._attrs.clear()
        self._attrs.update(value)

    def get_class_string(self, classes_to_add=None):
        """
        return a string that represents all the classes in attrs dict + obj attr classes
        :param classes_to_add:
        :param classes:
        :return:
        """
        if classes_to_add is None:
            classes_to_add = []
        _classes_to_add = []
        for cls in classes_to_add:
            if cls not in self.__class__.classes:
                _classes_to_add.append(cls)
        return f"class=\"{' '.join(self.__class__.classes)} {' '.join(_classes_to_add)}\""

    @staticmethod
    def generate_id():
        return f"{str(uuid.uuid4())}"

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
            if hasattr(self, 'parent') and self.parent is not None:
                # hasattr is for compatibility with django forms' deepcopy() approach
                self.parent.needs_render_recache = True

    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        """
        Central entry-point used by Django when it needs the widget’s HTML.

        * If caching is OFF      → always rebuild.
        * If caching is ON       → rebuild only when one of the “cache-relevant”
                                   attributes mutated or when the caller supplies
                                   per-instance attrs (which makes the output
                                   unique anyway).
        The actual HTML is produced by the subclass’ _render().
        """
        cache_enabled = getattr(settings, "BFE_WIDGET_CACHE", False)

        # 1.  No cache at all  ➜  recompute every time
        if not cache_enabled:
            return self._render(name, value, attrs=attrs, renderer=renderer, **kwargs)

        # 2.  Cache is enabled – but caller passed ad-hoc attrs
        #     (Django does this in form rendering).  Treat as “uncached”.
        if attrs:
            return self._render(name, value, attrs=attrs, renderer=renderer, **kwargs)

        # 3.  Cache path
        if self._needs_render_recache or self.cached_render == "":
            self.cached_render = self._render(
                name,
                value,
                attrs=attrs,
                renderer=renderer,
                **kwargs,
            )
            self._needs_render_recache = False

        return self.cached_render

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        return self.cached_render

    @property
    def media(self):
        """
        Returns a django.forms.widgets.Media instance that aggregates this
        widget’s own CSS/JS and all its descendants’.

        When caching is OFF the aggregation is rebuilt on *every* access.
        When caching is ON the aggregation is rebuilt only when one of the
        children signals it needs a recache.
        """
        cache_enabled = getattr(settings, "BFE_WIDGET_CACHE", False)

        if not cache_enabled:
            # Always recompute – simplest & safest while cache is disabled.
            return self._compute_media()

        # Cache enabled – rebuild only if invalidated.
        if self._needs_media_recache or self.cached_media is None:
            self.cached_media = self._compute_media()
            self._needs_media_recache = False

        return self.cached_media

    def _compute_media(self):
        if not getattr(settings, "BFE_WIDGET_CACHE", False):
            # No caching → recompute every call.
            own_media = Media(css=self.Media.css, js=self.Media.js)
            child_medias = [child.media for child in self.children.values()
                            if hasattr(child, 'media')]
            for cm in child_medias:
                own_media += cm
            return own_media
        else:
            raise NotImplementedError(
                "Widget-level caching is ON, but the cache backend "
                "is not implemented yet.  Disable BFE_WIDGET_CACHE "
                "or implement the backend before deploying."
            )

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    class Media:
        css = {}
        js = ()


"""
class SecretToggleCharWidget(BFEBaseWidget, Widget):
    aria_label = "Toggle Secret Field Visibility"
    DEFAULT_NAME = "secret_field_widget"

    def __init__(self, attrs=None, parent=None, **kwargs):
        \"""
        Initializes the widget.

        :param attrs: HTML attributes for the widget.
        :param input_type: The type of the input (default is 'password').
        \"""
        super().__init__(attrs=attrs, parent=parent, **kwargs)
        existing_classes = self.attrs.get('class', '')
        self.placeholder = self.attrs.get('placeholder', '')
        updated_classes = f"{existing_classes} secret-entry-field".strip()
        attrs['class'] = updated_classes  # todo: is this needed?

    def _render(self, name, value, attrs=None, renderer=None, **kwargs):
        \"""
        Renders the widget as HTML with a toggle button.

        :param name: The name of the input.
        :param value: The value of the input.
        :param attrs: Additional HTML attributes.
        :param renderer: The renderer to use.
        :return: Safe HTML string.
        \"""
        if attrs is None:
            attrs = self.attrs
        value = attrs.get('value', self.value)
        label = attrs.get('label', self.value)
        attrs['type'] = 'password'
        unique_id = attrs.get('id', self.generate_id())
        placeholder = attrs.get('placeholder', self.placeholder)
        extra_str = ''
        if placeholder:
            extra_str += f" placeholder=\"{placeholder}\""
        required = attrs.get('required', self.required)
        if required:
            extra_str += f" required"

        if not self.is_in_form:
            label_html = f'<label for="secret-field_{unique_id}" style="display:block;">{label}</label>\n'
        else:
            label_html = ''

        input_html = f'''
        <input type="password"
            class="secret-entry-field"
            id="secret-field_{unique_id}"
            name="{name}">'''

        if extra_str:
            input_html = input_html[:-1] + f' {extra_str}>'

        if value is not None:
            input_html = input_html[:-1] + f' value="{value}">'

        # Render the toggle button with unique data attributes
        toggle_html = \
            f'''
            <button class="secret-entry-toggle" type="button"
                data-bs-toggle="password"
                data-target="#secret-field_{unique_id}"
                data-icon="#icon_{unique_id}"
                aria-label="{self.aria_label}">
                <i class="eye-icon eye-closed" id="icon_{unique_id}"></i>
            </button>
            '''

        # Combine input and toggle button
        full_html = f'''
            <div class="secret-input-wrapper" style="position: relative;">
                {label_html}
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
                 edit_visible: bool = True, view_visible: bool = True, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
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

    def render(self, attrs=None, renderer=None, **kwargs):  # old: (self, name, value, attrs=None, renderer=None)
        \"""
        Renders the widget as HTML with a toggle button.

        :param name: The name of the input.
        :param value: The value of the input.
        :param attrs: Additional HTML attributes.
        :param renderer: The renderer to use.
        :return: Safe HTML string.
        \"""
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
"""
