from django import forms
from byefrontend.widgets import SecretToggleCharWidget


class SecretTestForm(forms.Form):
    secret_field_1 = forms.CharField(
        label="Secret Field 1",
        widget=SecretToggleCharWidget(attrs={'placeholder': 'Enter secret 1'}, is_in_form=True)
    )
    secret_field_2 = forms.CharField(
        label="Secret Field 2",
        widget=SecretToggleCharWidget(attrs={'placeholder': 'Enter secret 2'}, is_in_form=True)
    )


class UploadFileForm(forms.Form):
    file = forms.FileField()
