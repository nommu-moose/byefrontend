from django.shortcuts import render
from django.urls import reverse

from byefrontend.widgets import HyperlinkWidget
from byefrontend.widgets.containers import NavBarWidget
from byefrontend.widgets.files import FileUploadWidget
from .forms import SecretTestForm
from byefrontend.render import render_with_automatic_static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
import os


def basic_view(request):
    form = SecretTestForm()
    config = {
        'selected_path': ['about', 'further_dropdown'],
        'name': 'top_nav',
        'text': 'Home',
        'link': '/',
        'title_button': True,
        'children': {
            'home': {'type': 'HyperlinkWidget', 'text': 'Home', 'link': '/'},
            'about': {
                'name': 'about',
                'type': 'NavBarWidget',
                'text': 'About',
                'children': {
                    'team': {'type': 'HyperlinkWidget', 'text': 'Team', 'link': '/about/team'},
                    'company': {'type': 'HyperlinkWidget', 'text': 'Company', 'link': '/about/company'},
                    'further_dropdown': {
                        'name': 'further_dropdown',
                        'type': 'NavBarWidget',
                        'text': 'Further Dropdown',
                        'children': {
                            'bottom_button': {'type': 'HyperlinkWidget', 'text': 'Bottom', 'link': '/about/bottom'},
                        }
                    },
                    'bottom_dropdown': {
                        'name': 'bottom_dropdown',
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
    upload = FileUploadWidget()
    navbar = NavBarWidget(config=config)
    context = {'form': form, 'navbar': navbar, 'upload': upload, 'upload_url': reverse('upload_file')}
    return render_with_automatic_static(request, 'basic_view.html', context)


@csrf_exempt
def upload_file(request):
    print("this worked woo \n\n\n\n\n\n\n\n\n")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle file here
            handle_uploaded_file(request.FILES['file'])
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)


def handle_uploaded_file(f):
    # Define the upload directory
    upload_dir = 'uploaded_files/'

    # Create the directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the file to disk, for example
    with open('uploaded_files/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
