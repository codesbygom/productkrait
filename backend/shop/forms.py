from django import forms
from django.utils.text import slugify
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from .imaging import (
    PRODUCT_IMAGE_MAX_BYTES,
    PRODUCT_IMAGE_MIN_SIZE,
    PRODUCT_IMAGE_SIZE,
    normalize_product_image,
)
from .models import Product, Category, Order


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""
    class Meta:
        model = Product
        fields = ['title', 'price', 'discount_price', 'category', 'description', 'image', 'quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.CheckboxSelectMultiple(),
            'quantity': forms.NumberInput(attrs={'min': 0}),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'data-width': PRODUCT_IMAGE_SIZE[0],
                'data-height': PRODUCT_IMAGE_SIZE[1],
                'data-min-width': PRODUCT_IMAGE_MIN_SIZE[0],
                'data-min-height': PRODUCT_IMAGE_MIN_SIZE[1],
            }),
        }
        labels = {
            'title': 'Product title',
            'price': 'Price',
            'discount_price': 'Discounted price',
            'category': 'Category',
            'description': 'Description',
            'image': 'Product image',
            'quantity': 'Stock quantity',
        }
        help_texts = {
            'discount_price': 'Enter the discounted price (optional)',
            'category': 'Select the product categories',
            'description': 'Enter the full product description',
            'image': f'Photos are cropped to {PRODUCT_IMAGE_SIZE[0]}x{PRODUCT_IMAGE_SIZE[1]} (4:3), the shape shown in the shop.',
            'quantity': 'Enter the quantity of this product in stock',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Unchanged image on edit comes back as the stored file: keep it.
        if not isinstance(image, UploadedFile):
            return image
        if image.size > PRODUCT_IMAGE_MAX_BYTES:
            raise forms.ValidationError('The image is too large (max %d MB).' % (PRODUCT_IMAGE_MAX_BYTES // (1024 * 1024)))
        width, height = Image.open(image).size
        image.seek(0)
        min_w, min_h = PRODUCT_IMAGE_MIN_SIZE
        if width < min_w or height < min_h:
            raise forms.ValidationError(f'The image is too small ({width}x{height}). Minimum is {min_w}x{min_h}.')
        return normalize_product_image(image)

    def save(self, commit=True):
        product = super().save(commit=False)
        if 'image' in self.changed_data:
            product.thumbnail = None  # rebuilt lazily from the new image
        if not product.slug:
            product.slug = slugify(product.title) or 'product'
        if commit:
            product.save()
            self.save_m2m()
        return product


class OrderUpdateForm(forms.ModelForm):
    """Form for updating order status and tracking code."""
    class Meta:
        model = Order
        fields = ('status', 'tracking_code')
        widgets = {
            'tracking_code': forms.TextInput(attrs={'placeholder': 'Enter the shipping tracking code'}),
        }
        labels = {
            'status': 'Order status',
            'tracking_code': 'Tracking code',
        }


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""
    class Meta:
        model = Category
        fields = ('title', 'slug', 'parent', 'position', 'status')
        help_texts = {
            'slug': 'Used in the URL. Leave empty to generate it from the title.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        if self.instance.pk:
            excluded = [self.instance.pk] + [c.pk for c in self.instance.get_all_children()]
            self.fields['parent'].queryset = Category.objects.exclude(pk__in=excluded)
