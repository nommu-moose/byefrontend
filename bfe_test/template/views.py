from django.shortcuts import render

from byefrontend.widgets import HyperlinkWidget
from byefrontend.widgets.containers import NavBarWidget
from .forms import SecretTestForm
from byefrontend.render import render_with_automatic_static


def basic_view(request):
    form = SecretTestForm()
    config = {
        'selected_path': ['about', 'further_dropdown'],
        'title': 'My Site',
        'text': 'Home',
        'children': {
            'home': {'type': 'HyperlinkWidget', 'text': 'Home', 'link': '/'},
            'about': {
                'type': 'NavBarWidget',
                'text': 'About',
                'children': {
                    'team': {'type': 'HyperlinkWidget', 'text': 'Team', 'link': '/about/team'},
                    'company': {'type': 'HyperlinkWidget', 'text': 'Company', 'link': '/about/company'},
                    'further_dropdown': {
                        'type': 'NavBarWidget',
                        'text': 'Further Dropdown',
                        'children': {
                            'bottom_button': {'type': 'HyperlinkWidget', 'text': 'Bottom', 'link': '/about/bottom'},
                        }
                    },
                    'bottom_dropdown': {
                        'type': 'NavBarWidget',
                        'text': 'Bottom Dropdown',
                        'children': {
                            'bottom_button': {'type': 'HyperlinkWidget', 'text': 'Bottom', 'link': '/about/bottom'},
                        }
                    }
                }
            },
            'contact': {'type': 'HyperlinkWidget', 'text': 'Contact', 'link': '/contact'},
        }
    }
    navbar = NavBarWidget(config=config)
    context = {'form': form, 'navbar': navbar}
    return render_with_automatic_static(request, 'basic_view.html', context)
