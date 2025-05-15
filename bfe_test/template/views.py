# bfe_test/template/views.py
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ── ByeFrontend imports — use the *dataclass* configs ────────────────
from byefrontend.configs import (
    NavBarConfig,
    HyperlinkConfig,
    FileUploadConfig,
)
from byefrontend.widgets import NavBarWidget, FileUploadWidget
from byefrontend.render import render_with_automatic_static

from .forms import SecretTestForm, UploadFileForm

import os


def basic_view(request):
    """
    Render the demo page that shows:
      • a hierarchical NavBar
      • two Secret fields inside a Django form
      • the drag-and-drop FileUpload widget
    """
    # ── Django form ----------------------------------------------------
    form = SecretTestForm()

    # ── NavBar hierarchy (all configs, no dicts) ----------------------
    navbar_cfg = NavBarConfig(
        name="top_nav",
        text="ByeFrontend Demo",
        title_button=True,                 # makes the title the 1st button
        selected_id="further_dropdown",    # pre-open this path
        children={
            "home": HyperlinkConfig(text="Home",   link="/"),
            "about": NavBarConfig(
                name="about",
                text="About",
                children={
                    "team":     HyperlinkConfig(text="Team",    link="/about/team"),
                    "company":  HyperlinkConfig(text="Company", link="/about/company"),
                    "further_dropdown": NavBarConfig(
                        name="further_dropdown",
                        text="Further Dropdown",
                        children={
                            "bottom_button": HyperlinkConfig(text="Bottom", link="/about/bottom"),
                        },
                    ),
                    "bottom_dropdown": NavBarConfig(
                        name="bottom_dropdown",
                        text="Bottom Dropdown",
                        children={
                            "bottom_button": HyperlinkConfig(text="Bottom", link="/about/bottom"),
                        },
                    ),
                },
            ),
            "contact": HyperlinkConfig(text="Contact", link="/contact"),
        },
    )
    navbar = NavBarWidget(config=navbar_cfg)

    # ── File-upload widget --------------------------------------------
    upload_cfg = FileUploadConfig(
        upload_url=reverse("upload_file"),
        widget_html_id="my_upload_widget",
        filetypes_accepted=("image/png", "image/jpeg"),
        auto_upload=False,
        can_upload_multiple_files=True,
    )
    upload = FileUploadWidget(config=upload_cfg)

    # ── Render with automatic media aggregation -----------------------
    context = {
        "form": form,
        "navbar": navbar,
        "upload": upload,
        "upload_url": reverse("upload_file"),
    }
    return render_with_automatic_static(request, "basic_view.html", context)


# ---------------------------------------------------------------------#
#  Ajax endpoint used by the FileUpload widget                         #
# ---------------------------------------------------------------------#
@csrf_exempt
def upload_file(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Only POST requests are allowed"}, status=405
        )

    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    # Extra metadata sent by the widget
    file_name = request.POST.get("file_name") or request.FILES["file"].name
    file_path = request.POST.get("file_path", "")

    saved_path = _save_uploaded_file(request.FILES["file"], file_name)

    return JsonResponse(
        {
            "status": "success",
            "filepath": saved_path,       # returned to JS → shown in the table
            "file_name": file_name,
            "original_file_path": file_path,
        }
    )


def _save_uploaded_file(django_file, dst_name):
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, dst_name)
    with open(full_path, "wb+") as destination:
        for chunk in django_file.chunks():
            destination.write(chunk)

    # Media isn’t served in this demo → just return the relative path
    return f"/{upload_dir}/{dst_name}"
