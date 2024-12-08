from django.urls import path
from . import views

urlpatterns = [
    path('', views.basic_view, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
]
