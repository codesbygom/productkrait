from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404
from ..models import Product, Category


class CategoriesContextMixin:
    """Adds the active categories every shop page shows."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.active()
        return context


class IndexView(CategoriesContextMixin, ListView):
    """View for displaying all products."""
    template_name = 'shop/index.html'
    context_object_name = 'product_obj'
    paginate_by = 8

    def get_queryset(self):
        """Get products with optional search filter."""
        products = Product.objects.prefetch_related('category')
        search_query = self.request.GET.get('item_name')
        if search_query:
            products = products.search(search_query)
        return products


class ProductDetailView(CategoriesContextMixin, DetailView):
    """View for displaying product details."""
    model = Product
    pk_url_kwarg = 'id'
    template_name = 'shop/detail.html'
    context_object_name = 'product_obj'


class CategoryView(CategoriesContextMixin, ListView):
    """View for displaying products in a category."""
    template_name = 'shop/category.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        """Get products in category."""
        self.category = get_object_or_404(Category.objects.active(), slug=self.kwargs['slug'])
        return Product.objects.in_category(self.category).prefetch_related('category')

    def get_context_data(self, **kwargs):
        """Add category to context."""
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.category
        return context


class SearchView(CategoriesContextMixin, ListView):
    """View for displaying search results."""
    template_name = 'shop/search.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        """Get products matching search query."""
        search_query = self.request.GET.get('q')
        if not search_query:
            return Product.objects.none()
        return Product.objects.search(search_query).prefetch_related('category')

    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CategoriesView(TemplateView):
    """View for displaying all categories in a dedicated page."""
    template_name = 'shop/categories_page.html'

    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['categories_tree'] = Category.objects.active().roots().prefetch_related(
            'children__children__children__children__children'
        )
        return context
