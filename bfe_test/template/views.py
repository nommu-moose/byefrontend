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
        'can_upload_multiple_files': True
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
    if request.method == 'POST':
        # Extract metadata from request.POST
        # The widget sends these fields as additional form data along with the file.
        file_name = request.POST.get('file_name', None)
        file_path = request.POST.get('file_path', None)

        # Initialize and validate the form with the uploaded file
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            # If a custom file_name was provided by the user in the widget,
            # use that as the final saved filename. Otherwise use the original name.
            saved_file_name = file_name if file_name else uploaded_file.name

            # Handle the actual file saving
            saved_path = handle_uploaded_file(uploaded_file, saved_file_name)

            # Return JSON with success info, including the chosen filename and filepath
            return JsonResponse({
                'status': 'success',
                'filepath': saved_path,          # The URL or path to the uploaded file on the server
                'file_name': saved_file_name,    # The final name we saved the file as
                'original_file_path': file_path   # Echo back what was provided (if you want)
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)


def handle_uploaded_file(f, custom_name=None):
    upload_dir = 'uploaded_files/'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Use the custom name if provided, otherwise fall back to the file's original name
    filename = custom_name if custom_name else f.name
    full_path = os.path.join(upload_dir, filename)

    with open(full_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Return a path or URL to the uploaded file (this can be a URL if you have media served)
    return f"/uploaded_files/{filename}"
