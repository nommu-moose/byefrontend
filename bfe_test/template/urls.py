from django.urls import path
from . import views

urlpatterns = [
    path('', views.basic_view, name='home'),
]
