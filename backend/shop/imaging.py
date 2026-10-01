"""Product image format.

Every product photo is stored at exactly PRODUCT_IMAGE_SIZE (4:3). The shop
shows it in 4:3 frames (cards and detail page), so what staff crop in the
manager is what customers see. Change the size here and the manager crop
box, the server-side normalisation and the thumbnail all follow.
"""
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

PRODUCT_IMAGE_SIZE = (1200, 900)
PRODUCT_IMAGE_MIN_SIZE = (600, 450)
PRODUCT_THUMBNAIL_SIZE = (400, 300)
PRODUCT_IMAGE_MAX_BYTES = 5 * 1024 * 1024

PRODUCT_IMAGE_RATIO = PRODUCT_IMAGE_SIZE[0] / PRODUCT_IMAGE_SIZE[1]


def normalize_product_image(image_file):
    """Return a ContentFile: `image_file` cropped (centred) and resized to
    PRODUCT_IMAGE_SIZE as JPEG. Transparent areas become white."""
    img = ImageOps.exif_transpose(Image.open(image_file))
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.getchannel('A'))
        img = background
    else:
        img = img.convert('RGB')

    img = ImageOps.fit(img, PRODUCT_IMAGE_SIZE, Image.LANCZOS, centering=(0.5, 0.5))

    out = BytesIO()
    img.save(out, 'JPEG', quality=90, optimize=True)
    return ContentFile(out.getvalue(), name='product.jpg')
