"""
untested as yet, use at own peril
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EncryptedUnlockKey, EncryptedSecret
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


@login_required
def unlock_key_view(request, key_id):
    if request.method == "POST":
        password = request.POST.get('password')
        euk = EncryptedUnlockKey.objects.get(id=key_id, is_active=True)

        # Check user or group access:
        if not (euk.allowed_users.filter(id=request.user.id).exists() or
                euk.allowed_groups.filter(id__in=request.user.groups.all()).exists()):
            raise PermissionDenied("You do not have permission to unlock this key.")

        try:
            unlock_key = euk.unlock_key(password)
            # Store the unlocked key in session (base64 encode to store)
            import base64
            request.session[f'unlock_key_{key_id}'] = base64.b64encode(unlock_key).decode('utf-8')
            return redirect('view_secrets', key_id=key_id)
        except Exception:
            return HttpResponse("Invalid password.", status=403)

    return render(request, 'unlock_key.html', {'key_id': key_id})


@login_required
def view_secrets(request, key_id):
    # Check if unlock key is in session:
    unlock_key_b64 = request.session.get(f'unlock_key_{key_id}')
    if not unlock_key_b64:
        return HttpResponse("Key not unlocked.", status=403)
    import base64
    unlock_key = base64.b64decode(unlock_key_b64)

    euk = EncryptedUnlockKey.objects.get(id=key_id)
    secrets = euk.secrets.all()
    decrypted_data = []
    for s in secrets:
        plaintext = s.decrypt_secret(unlock_key)
        # Assume plaintext is UTF-8 text
        decrypted_data.append(plaintext.decode('utf-8'))

    return render(request, 'view_secrets.html', {'secrets': decrypted_data})
