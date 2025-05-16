# bfe_test/template/views.py
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from django import forms
from django.middleware.csrf import get_token
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django import forms
from django.urls import reverse

from byefrontend.render import render_with_automatic_static

# ① widgets & configs
from byefrontend.widgets import (
    CheckBoxWidget, RadioWidget, CodeBoxWidget, LabelWidget,
    TableWidget, PopOut, TinyThumbnailWidget,
    TitleWidget, HyperlinkWidget, NavBarWidget, SecretToggleCharWidget,
    FileUploadWidget, RadioGroupWidget, InlineGroupWidget, CharInputWidget, TextEditorWidget, InlineFormWidget
)
from byefrontend.configs import (
    TableConfig, NavBarConfig, HyperlinkConfig, FileUploadConfig,
    SecretToggleConfig, PopOutConfig, ThumbnailConfig, TitleConfig,
    RadioGroupConfig, CheckBoxConfig, LabelConfig, InlineGroupConfig,
    TextInputConfig, DropdownConfig, DatePickerConfig, InlineFormConfig
)

from byefrontend.storage import get_storage

from byefrontend.render import render_with_automatic_static
from byefrontend.widgets.datepicker import DatePickerWidget
from byefrontend.widgets.dropdown import DropdownWidget
from byefrontend.widgets.radio_group import RadioGroupWidget

from .forms import SecretTestForm, UploadFileForm


from django.shortcuts import redirect, render
from django.urls import reverse

from byefrontend.widgets import BFEFormWidget
from byefrontend.configs import (
    FormConfig, TextInputConfig, TextEditorConfig, tweak
)
from .models import Feedback
from byefrontend.render import render_with_automatic_static

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
                            "widgets_button": HyperlinkConfig(text="Widgets", link="/widgets/"),
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
            "feedback": HyperlinkConfig(text="Feedback", link="/feedback/"),
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
@require_POST
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


def _save_uploaded_file(django_file, original_name: str) -> str:
    """
    Save via Django’s Storage API – works with local FS, S3,
    encrypted back-ends, you name it.
    """
    storage = get_storage()

    ext       = Path(original_name).suffix.lower()        # keep .png / .jpg
    safe_name = f"{uuid4().hex}{ext}"                     # collision-safe
    saved_rel = storage.save(safe_name, django_file)      # <subdir>/xxxxx.png

    return storage.url(saved_rel)                         # absolute /media/…


def widgets_demo(request):
    """
    One page that puts every widget on screen so you can eyeball
    rendering, JS behaviour & aggregated static files in one go.
    """
    # --- individual widget instances ---------------------------------
    checkbox   = CheckBoxWidget()
    radio      = radio_group = RadioGroupWidget(
        config=RadioGroupConfig(
            title="Radio Group",
            name="demo_group",
            choices=[("A", "Choice A"), ("B", "Choice B"), ("C", "Choice C")],
            selected="A",
            layout="inline",
        )
    )
    code_box   = CodeBoxWidget(language="python", value="print('hello world')")
    label      = LabelWidget(text="Plain label pointing nowhere")
    title      = TitleWidget(config=TitleConfig(text="ByeFrontend widgets demo", level=2))
    thumbnail  = TinyThumbnailWidget(config=ThumbnailConfig(src="/static/byefrontend/img/icons/open-eye.png",
                                                            alt="sample"))
    popout     = PopOut(config=PopOutConfig(trigger_text="Open pop-out", title="Hello!"))
    hyperlink  = HyperlinkWidget(config=HyperlinkConfig(text="External link",
                                                        link="https://www.example.com"))
    # --- table & sample data -----------------------------------------
    tbl_cfg = TableConfig(
        fields=[
            {"field_name": "name", "field_text": "Name", "field_type": "text"},
            {"field_name": "age",  "field_text": "Age",  "field_type": "text"},
        ],
        data=[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    )
    table      = TableWidget(config=tbl_cfg)

    # --- navbar, secret field & file-upload are already demoed elsewhere,
    #     but include them here too so *everything* is on one page -------
    navbar_cfg = NavBarConfig(
        text="Widget sampler",
        title_button=True,
        children={
            "home": HyperlinkConfig(text="Home", link=reverse("home")),
            "docs": HyperlinkConfig(text="Docs", link="https://github.com/nommu-moose/byefrontend"),
        },
    )
    navbar      = NavBarWidget(config=navbar_cfg)

    secret_cfg  = SecretToggleConfig(is_in_form=False, placeholder="Type a secret")
    secret      = SecretToggleCharWidget(config=secret_cfg)

    fu_cfg = FileUploadConfig(
        upload_url=reverse("upload_file"),
        widget_html_id="demo_upload",
        auto_upload=True,
    )
    upload_widget = FileUploadWidget(config=fu_cfg)

    group_cfg = InlineGroupConfig(
        children={
            "user": TextInputConfig(placeholder="username"),
            "sep": LabelConfig(text="a label"),
            "token": SecretToggleConfig(placeholder="API token"),
        },
        classes=("equal-width",),
        gap=1,
    )

    inlinegroup = InlineGroupWidget(config=group_cfg)

    datepicker = DatePickerWidget(
        config=DatePickerConfig(placeholder="YYYY-MM-DD")
    )

    dropdown = DropdownWidget(
        config=DropdownConfig(
            placeholder="Choose a flavour",
            choices=[("vanilla", "Vanilla"), ("choc", "Chocolate")],
            selected="choc",
        )
    )

    text_editor = TextEditorWidget()

    children_cfg = get_feedback_children_cfg()

    form_cfg = FormConfig(
        action=reverse("feedback"),  # POST back to the same URL
        csrf=True,
        children=children_cfg,
    )

    bfe_form = BFEFormWidget(
        config=form_cfg,
        request=request,  # needed so BYE-Frontend can inject CSRF
        data=request.POST or None,
    )

    inline_form_cfg = InlineFormConfig.build(
        action=reverse("feedback"),
        csrf=True,
        children=children_cfg,
    )

    inline_form = InlineFormWidget(config=inline_form_cfg, request=request)

    ctx = {
        "checkbox": checkbox,
        "radio": radio,
        "code_box": code_box,
        "label": label,
        "title": title,
        "thumbnail": thumbnail,
        "popout": popout,
        "hyperlink": hyperlink,
        "table": table,
        "navbar": navbar,
        "secret": secret,
        "upload": upload_widget,
        "inlinegroup": inlinegroup,
        "datepicker": datepicker,
        "dropdown": dropdown,
        "text_editor": text_editor,
        "bfe_form": bfe_form,
        "inline_form": inline_form,
    }
    return render_with_automatic_static(request, "widgets_demo.html", ctx)


def get_feedback_children_cfg():
    children_cfg = {
        "name":   TextInputConfig(
            label="Your name", placeholder="Ada Lovelace", required=True
        ),
        "email":  TextInputConfig(
            label="E-mail", input_type="email", placeholder="ada@example.com",
            required=True
        ),
        "message": TextEditorConfig(
            placeholder="Tell us what's on your mind …"
        ),
    }
    return children_cfg


def feedback_view(request):
    """
    Renders the Bye-Frontend composable form **and** handles the POST.
    Watch your Django run-server console for print-outs.
    """
    # ---------- build the form widget ---------------------------------
    children_cfg = get_feedback_children_cfg()

    form_cfg = FormConfig(
        action=reverse("feedback"),   # POST back to the same URL
        csrf=True,
        children=children_cfg,
    )

    bfe_form = BFEFormWidget(
        config=form_cfg,
        request=request,         # needed so BYE-Frontend can inject CSRF
        data=request.POST or None,
    )

    # ---------- POST? then validate & save ----------------------------
    if request.method == "POST":
        print("🔍 Incoming POST →", dict(request.POST))            # debug helper
        if bfe_form.is_valid():
            cd = bfe_form.cleaned_data
            fb = Feedback.objects.create(
                name=cd["name"],
                email=cd["email"],
                message=cd["message"],
            )
            print("✅ Saved feedback object:", fb)                 # debug helper
            return redirect("feedback_thanks")

        print("❌ Form errors:", bfe_form.errors)                  # debug helper

    # ---------- render -------------------------------------------------
    ctx = {"bfe_form": bfe_form}
    return render_with_automatic_static(request, "feedback.html", ctx)


def feedback_thanks_view(request):
    return render(request, "feedback_thanks.html")

