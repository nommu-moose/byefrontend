from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps


def require_logged_out(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('container_list'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_admin(view_func):
    # todo: custom flags from settings.py
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if getattr(request.user, "is_superuser", False) or getattr(request.user, "is_staff", False):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("home"))
    return _wrapped_view


def require_uninitialised_site(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if settings.master_password is None:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('home'))
