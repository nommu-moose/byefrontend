from importlib import import_module
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def _build_default_fs():
    location = Path(settings.MEDIA_ROOT) / settings.BFE_FILE_UPLOAD_SUBDIR
    return FileSystemStorage(
        location=location,
        base_url=f'{settings.MEDIA_URL}{settings.BFE_FILE_UPLOAD_SUBDIR}/',
    )


def get_storage():
    """
    Return an *instance* of the storage class referenced by
    `settings.BFE_FILE_UPLOAD_STORAGE`.

    - Leave it pointing to FileSystemStorage for local dev.
    - Swap to `'storages.backends.s3boto3.S3Boto3Storage'`, Azure,
      GCS… without touching Upload-code.
    """
    dotted = getattr(settings, 'BFE_FILE_UPLOAD_STORAGE', None)
    if dotted and dotted != 'django.core.files.storage.FileSystemStorage':
        module_path, cls_name = dotted.rsplit('.', 1)
        storage_cls = getattr(import_module(module_path), cls_name)
        return storage_cls()
    return _build_default_fs()
