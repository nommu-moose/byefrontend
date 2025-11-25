from django.contrib import admin
from django.urls import path, include

# Import BFE registry (autodiscover happens lazily)
from byefrontend.model_views import bfe

urlpatterns = [
    path('', include('template.urls')),
    path('admin/', admin.site.urls),
    path('bfe/', include(bfe.urls)),  # autodiscovers bfe_views.py modules
]
