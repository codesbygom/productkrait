from django import forms
from django.utils.text import slugify
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
            'image': 'Select the product image',
            'quantity': 'Enter the quantity of this product in stock',
        }

    def save(self, commit=True):
        product = super().save(commit=False)
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
