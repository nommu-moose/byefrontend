class Table:
    scrollable = True

    def __init__(self):
        pass


class NavBar:
    def __init__(self, attrs=None, *args, **kwargs):
        """
        Initializes the widget.

        :param attrs: HTML attributes for the widget.
        """
        if attrs is None:
            attrs = {}
        existing_classes = attrs.get('class', '')
        updated_classes = f"{existing_classes} bfe-navbar".strip()
        attrs['class'] = updated_classes
        super().__init__(attrs, *args, **kwargs)

    def __str__(self):
        pass

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


class PopOut:
    def __init__(self):
        pass
