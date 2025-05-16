from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.basic_view, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('widgets/', views.widgets_demo, name='widgets_demo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
