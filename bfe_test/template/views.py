from django.shortcuts import render
from .forms import SecretTestForm
from byefrontend.render import render_with_automatic_static


def basic_view(request):
    form = SecretTestForm()
    context = {'form': form}
    return render_with_automatic_static(request, 'basic_view.html', context)
