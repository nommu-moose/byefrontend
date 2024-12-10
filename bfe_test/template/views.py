from django.urls import reverse

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

    navbar = NavBarWidget(config=config)

    # Prepare configuration for FileUploadWidget
    upload_widget_config = {
        'upload_url': reverse('upload_file'),
        'widget_html_id': 'my_upload_widget',
        'filetypes_accepted': ['image/png', 'image/jpeg'],  # example file types
        'auto_upload': False,
        'can_upload_multiple_files': True,
        # Additional fields if not auto_upload
        # 'file_name' is included by default, but you can override or add more:
        'fields': [
            # file_name will be inserted automatically if not present
            {'field_name': 'description', 'editable': True, 'visible': True},
            {'field_name': 'tags', 'editable': True, 'visible': True}
        ]
    }

    upload = FileUploadWidget(config=upload_widget_config)

    context = {
        'form': form,
        'navbar': navbar,
        'upload': upload,
        'upload_url': reverse('upload_file'),
    }

    return render_with_automatic_static(request, 'basic_view.html', context)


@csrf_exempt
def upload_file(request):
    print("this worked woo \n\n\n\n\n\n\n\n\n")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle file here
            handle_uploaded_file(request.FILES['file'])
            return JsonResponse({'status': 'success', 'filepath': f"/uploaded_files/{request.FILES['file'].name}"})
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

    # Save the file to disk
    with open(os.path.join(upload_dir, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
