from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.basic_view, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('widgets/', views.widgets_demo, name='widgets_demo'),
    path("feedback/", views.feedback_view, name="feedback"),
    path("feedback/thanks/", views.feedback_thanks_view, name="feedback_thanks"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
