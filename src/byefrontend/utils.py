import uuid


def dict_null_values_to_defaults(target_dict, default_dict):
    for key, value in default_dict.items():
        if not target_dict.get(key):
            target_dict[key] = value
    return target_dict


def create_navbar_from_simple_site_structure(site_structure: dict, include_home_button: bool = True) -> dict:
    """
    Create a navbar config from a simplified site structure dict.
    Adds a home button by default.
    """
    navbar = {
        'name': 'top_nav',
        'type': 'NavBarWidget',
        'children': {}
    }

    if include_home_button:  # currently this has to be the case - need to edit js
        home_item = create_navbar_item('Home', '')
        navbar['children']['home'] = home_item

    for name, value in site_structure.items():
        item = create_navbar_item(name, value)
        item_key = item.get('name', name.lower().replace(' ', '_'))
        navbar['children'][item_key] = item

    return navbar


def create_navbar_item(name: str, value, navbar_items_are_unique=False) -> dict:
    """
    Recursively create a navbar item. If value is a dict, it's a NavBarWidget.
    Otherwise, it's a HyperlinkWidget.
    """
    base_name = name.lower().replace(' ', '_')
    if not navbar_items_are_unique:
        unique_name = f"{base_name}_{str(uuid.uuid4())[:8]}" if base_name != 'home' else base_name
    else:
        unique_name = base_name

    if isinstance(value, dict):
        children_dict = {}
        for child_name, child_value in value.items():
            child_item = create_navbar_item(child_name, child_value)
            child_key = child_item.get('name', name.lower().replace(' ', '_'))
            children_dict[child_key] = child_item

        return {
            'name': unique_name,
            'type': 'NavBarWidget',
            'text': name,
            'children': children_dict
        }
    else:
        link = '/' if base_name == 'home' else f"/{unique_name}"
        return {
            'type': 'HyperlinkWidget',
            'text': name,
            'link': link
        }
