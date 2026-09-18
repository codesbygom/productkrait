from django import forms
from .models import Product, Category

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