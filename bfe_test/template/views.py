from pathlib import Path
from uuid import uuid4
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from byefrontend.widgets import (
    CheckBoxWidget, CodeBoxWidget, LabelWidget,
    TableWidget, PopOut, TinyThumbnailWidget,
    TitleWidget, HyperlinkWidget, NavBarWidget, SecretToggleCharWidget,
    FileUploadWidget, InlineGroupWidget, TextEditorWidget, InlineFormWidget,
    ParagraphWidget, DocumentLinkWidget, DocumentViewerWidget, DataFilterWidget,
    TagInputWidget
)
from byefrontend.configs import (
    TableConfig, NavBarConfig, HyperlinkConfig, FileUploadConfig,
    SecretToggleConfig, PopOutConfig, ThumbnailConfig, TitleConfig,
    RadioGroupConfig, CheckBoxConfig, LabelConfig, InlineGroupConfig,
    DropdownConfig, DatePickerConfig, InlineFormConfig, ParagraphConfig, DocumentLinkConfig,
    DocumentViewerConfig, DataFilterConfig, TagInputConfig
)

from byefrontend.storage import get_storage
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
from .models import Feedback, DataForFiltering
from byefrontend.render import render_with_automatic_static


def basic_view(request):
    # to show compatibility with normal django forms
    form = SecretTestForm()

    navbar_cfg = NavBarConfig(
        name="top_nav",
        text="ByeFrontend Demo",
        title_button=True,
        selected_id="further_dropdown",
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
                            "data": HyperlinkConfig(text="Data", link="/data/"),
                        },
                    ),
                },
            ),
            "feedback": HyperlinkConfig(text="Feedback", link="/feedback/"),
        },
    )
    navbar = NavBarWidget(config=navbar_cfg)

    upload_cfg = FileUploadConfig(
        upload_url=reverse("upload_file"),
        widget_html_id="my_upload_widget",
        filetypes_accepted=("image/png", "image/jpeg"),
        auto_upload=False,
        can_upload_multiple_files=True,
    )
    upload = FileUploadWidget(config=upload_cfg)

    context = {
        "form": form,
        "navbar": navbar,
        "upload": upload,
        "upload_url": reverse("upload_file"),
    }
    return render_with_automatic_static(request, "basic_view.html", context)


@require_POST
def upload_file(request):
    """Ajax endpoint used by the FileUpload widget"""
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
            "filepath": saved_path,  # returned to JS -> shown in the table
            "file_name": file_name,
            "original_file_path": file_path,
        }
    )


def _save_uploaded_file(django_file, original_name: str) -> str:
    """
    Save via Django’s Storage API – works with local FS, S3, encrypted back-ends, you name it.
    """
    storage = get_storage()

    ext = Path(original_name).suffix.lower()
    safe_name = f"{uuid4().hex}{ext}"  # collision safety
    saved_rel = storage.save(safe_name, django_file)

    return storage.url(saved_rel)


def widgets_demo(request):
    """
    One page that puts every widget on screen to eyeball
    rendering, JS behaviour & aggregated static files in one go.
    """
    checkbox = CheckBoxWidget()
    radio = RadioGroupWidget(
        config=RadioGroupConfig(
            title="Radio Group",
            name="demo_group",
            choices=[("A", "Choice A"), ("B", "Choice B"), ("C", "Choice C")],
            selected="A",
            layout="inline",
        )
    )
    code_box = CodeBoxWidget(language="python", value="print('hello world')")
    label = LabelWidget(text="Plain label pointing nowhere")
    title = TitleWidget(config=TitleConfig(text="ByeFrontend widgets demo", level=2))
    thumbnail = TinyThumbnailWidget(config=ThumbnailConfig(src="/static/byefrontend/img/icons/open-eye.png",
                                                           alt="sample"))
    sample_pdf = "/uploads/sample_pdf.pdf"

    doc_link = DocumentLinkWidget(
        config=DocumentLinkConfig(file_url=sample_pdf,
                                  label="Download sample PDF")
    )

    viewer_widget = DocumentViewerWidget(
        config=DocumentViewerConfig(file_url=sample_pdf,
                                    height_rem=48)
    )

    doc_popout = PopOut(
        config=PopOutConfig(trigger_text="Open PDF Viewer",
                            title="Sample PDF"),
        content=viewer_widget
    )

    popout = PopOut(config=PopOutConfig(trigger_text="Open pop-out", title="Hello!"))
    hyperlink = HyperlinkWidget(config=HyperlinkConfig(text="External link", link="https://www.example.com"))
    tbl_cfg = TableConfig(
        fields=[
            {"field_name": "name", "field_text": "Name", "field_type": "text"},
            {"field_name": "age",  "field_text": "Age",  "field_type": "text"},
        ],
        data=[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    )
    table = TableWidget(config=tbl_cfg)

    navbar_cfg = NavBarConfig(
        text="Widget sampler",
        title_button=True,
        children={
            "home": HyperlinkConfig(text="Home", link=reverse("home")),
            "docs": HyperlinkConfig(text="Docs", link="https://github.com/nommu-moose/byefrontend"),
        },
    )
    navbar = NavBarWidget(config=navbar_cfg)

    secret_cfg = SecretToggleConfig(is_in_form=False, placeholder="Type a secret")
    secret = SecretToggleCharWidget(config=secret_cfg)

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

    tag_input = TagInputWidget(
        config=TagInputConfig(
            placeholder="Add tags",
            suggestions=("alpha", "beta", "gamma", "delta"),
        )
    )

    lorem_ipsum = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Suspendisse gravida viverra magna sed consequat.
Nulla facilisi.
Vestibulum pretium, magna vitae varius fringilla, nulla urna tincidunt justo, eu placerat mauris purus quis tortor.
Ut consectetur in erat sit amet malesuada. In lacinia urna eu sollicitudin ultrices.
Pellentesque auctor, velit non tincidunt sagittis, turpis purus bibendum risus, et pellentesque orci augue vel mi.
Vestibulum nec iaculis arcu. Integer vel elit sed tortor mattis maximus non quis tortor.
    """

    inserted_text = "\n".join([f"<li>{line_text}</li>" for line_text in lorem_ipsum.strip().splitlines()])

    editor_cfg = tweak(TextEditorConfig(), value=inserted_text)
    text_editor = TextEditorWidget(config=editor_cfg)

    children_cfg = get_feedback_children_cfg()

    form_cfg = FormConfig(
        action=reverse("feedback"),
        csrf=True,
        children=children_cfg,
    )

    bfe_form = BFEFormWidget(
        config=form_cfg,
        request=request,  # NOTE: needed for bfe's csrf injection
        data=request.POST or None,
    )

    inline_form_cfg = InlineFormConfig.build(
        action=reverse("feedback"),
        csrf=True,
        children=children_cfg,
    )

    inline_form = InlineFormWidget(config=inline_form_cfg, request=request)

    para = ParagraphWidget(
        config=tweak(ParagraphConfig(), text=lorem_ipsum, align="center", italic=True)
    )

    prepop_inline_cfg = InlineFormConfig.build(
        action="",               # POST back to the same URL
        method="post",
        csrf=True,
        gap=0.75,                # 0.75 rem between fields
        wrap=True,
        children={
            "email": TextInputConfig(
                label="Email address",
                input_type="email",
                required=True,
            ),
            "api_key": SecretToggleConfig(
                label="API key",
                required=True,
            ),
            "joined": DatePickerConfig(
                label="Joined on",
            ),
        },
    )

    prepop_initial_data = {
        "email":   "demo@example.com",
        "api_key": "super-secret-123",
        "joined":  "2024-10-31",
    }

    prepop_inline_form = InlineFormWidget(
        config=prepop_inline_cfg,
        data=prepop_initial_data,
        request=request,
    )

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
        "tag_input": tag_input,
        "text_editor": text_editor,
        "bfe_form": bfe_form,
        "inline_form": inline_form,
        "para": para,
        "doc_link": doc_link,
        "doc_popout": doc_popout,
        "prepop_inline_form": prepop_inline_form,
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
    """
    children_cfg = get_feedback_children_cfg()

    form_cfg = FormConfig(
        action=reverse("feedback"),
        csrf=True,
        children=children_cfg,
    )

    bfe_form = BFEFormWidget(
        config=form_cfg,
        request=request,
        data=request.POST or None,
    )

    if request.method == "POST":
        print("Incoming POST:", dict(request.POST))
        if bfe_form.is_valid():
            cd = bfe_form.cleaned_data
            fb = Feedback.objects.create(name=cd["name"], email=cd["email"], message=cd["message"])
            print("✅ Saved feedback object:", fb)
            return redirect("feedback_thanks")

        print("Form errors:", bfe_form.errors)

    ctx = {"bfe_form": bfe_form}
    return render_with_automatic_static(request, "feedback.html", ctx)


def feedback_thanks_view(request):
    return render(request, "feedback_thanks.html")


def data_explorer_view(request):
    """
    Server-side filtering + BYE-Frontend table for DataForFiltering.
    """
    q_name = request.GET.get("name", "").strip()
    q_domain = request.GET.get("domain", "").strip()
    q_active = request.GET.get("active_only") == "on"
    sort_by = request.GET.get("sort_by") or None
    sort_dir = request.GET.get("sort_dir", "asc")
    page = max(int(request.GET.get("page", 1)), 1)

    # building queryset
    qs = DataForFiltering.objects.all()
    if q_name:
        qs = qs.filter(name__icontains=q_name)
    if q_domain:
        qs = qs.filter(domain__icontains=q_domain)
    if q_active:
        qs = qs.filter(is_active=True)
    if sort_by in {"name", "domain", "created", "account_credits"}:
        order = sort_by if sort_dir == "asc" else f"-{sort_by}"
        qs = qs.order_by(order)

    rows = list(
        qs.values(
            "name", "domain", "created", "birthday",
            "is_active", "is_admin", "account_credits",
        )
    )

    filter_cfg = {
        "name":   TextInputConfig(label="Name contains", placeholder="Alice"),
        "domain": TextInputConfig(label="Domain contains", placeholder="example.com"),
        "active_only": CheckBoxConfig(label="Active only", checked=q_active),
        "sort_by": DropdownConfig(
            label="Sort by", is_in_form=False,
            choices=[
                ("name", "Name"), ("domain", "Domain"),
                ("created", "Created"), ("account_credits", "Credits"),
            ],
            selected=sort_by, placeholder="Sort by …"
        ),
        "sort_dir": DropdownConfig(
            label="Direction", is_in_form=False,
            choices=[("asc", "↑ Ascending"), ("desc", "↓ Descending")],
            selected=sort_dir, placeholder="Direction …",
        ),
    }

    table_fields = (
        {"field_name": "name",            "field_text": "Name",    "field_type": "text"},
        {"field_name": "domain",          "field_text": "Domain",  "field_type": "text"},
        {"field_name": "created",         "field_text": "Created", "field_type": "text"},
        {"field_name": "birthday",        "field_text": "Birthday","field_type": "text"},
        {"field_name": "is_active",       "field_text": "Active?", "field_type": "text"},
        {"field_name": "is_admin",        "field_text": "Admin?",  "field_type": "text"},
        {"field_name": "account_credits", "field_text": "Credits", "field_type": "text"},
    )

    df_cfg = DataFilterConfig(
        filters=filter_cfg,
        data=rows,
        table_fields=table_fields,
        page=page,
        page_size=25,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    datafilter = DataFilterWidget(config=df_cfg, request=request)

    ctx = {"datafilter": datafilter}
    return render_with_automatic_static(request, "data_explorer.html", ctx)
