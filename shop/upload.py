import os
import uuid

from django.utils.deconstruct import deconstructible


@deconstructible
class UUIDUploadTo:
    """`upload_to` that stores uploads as <folder>/<uuid4>.<ext>.

    The original filename is dropped: it can hold odd characters and collide
    with another upload. Deconstructible so migrations can serialize it.
    """

    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f'{self.folder}/{uuid.uuid4().hex}{ext}'
