from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from shop.forms import CategoryForm, OrderUpdateForm, ProductForm
from shop.models import Category, Order, OrderItem, Product

from .forms import StaffAuthenticationForm
from .mixins import StaffRequiredMixin

LOW_STOCK = 5


class ManagerLoginView(LoginView):
    template_name = 'manager/login.html'
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = False
    next_page = reverse_lazy('manager:dashboard')

    def get_success_url(self):
        return self.get_redirect_url() or str(self.next_page)


class ManagerLogoutView(LogoutView):
    next_page = reverse_lazy('manager:login')


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'manager/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            product_count=Product.objects.count(),
            category_count=Category.objects.count(),
            order_count=Order.objects.count(),
            pending_orders=Order.objects.filter(status='pending').count(),
            low_stock=Product.objects.filter(quantity__lte=LOW_STOCK).order_by('quantity')[:8],
            low_stock_limit=LOW_STOCK,
        )
        return ctx


class ProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = 'manager/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.prefetch_related('category')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ProductFormMixin(StaffRequiredMixin):
    model = Product
    form_class = ProductForm
    template_name = 'manager/product_form.html'
    success_url = reverse_lazy('manager:products')
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message.format(title=self.object.title))
        return response


class ProductCreateView(ProductFormMixin, CreateView):
    success_message = 'Product "{title}" created.'


class ProductUpdateView(ProductFormMixin, UpdateView):
    success_message = 'Product "{title}" updated.'


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'manager/product_confirm_delete.html'
    success_url = reverse_lazy('manager:products')

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'Product "{title}" deleted.')
        return response


class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = 'manager/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.select_related('user').order_by('-created_at')
        self.status = self.request.GET.get('status', '')
        if self.status in dict(Order.STATUS_CHOICES):
            qs = qs.filter(status=self.status)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(user__email__icontains=q) | Q(tracking_code__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(q=self.request.GET.get('q', ''), status=self.status, statuses=Order.STATUS_CHOICES)
        return ctx


class OrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = 'manager/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = OrderItem.objects.filter(order=self.object).select_related('product')
        return ctx


class OrderUpdateView(StaffRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'manager/order_form.html'

    def get_success_url(self):
        return reverse_lazy('manager:order-detail', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, f'Order #{self.object.pk} updated.')
        return super().form_valid(form)


class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = 'manager/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.select_related('parent').order_by('position', 'title')


class CategoryFormMixin(StaffRequiredMixin):
    model = Category
    form_class = CategoryForm
    template_name = 'manager/category_form.html'
    success_url = reverse_lazy('manager:categories')
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message.format(title=self.object.title))
        return response


class CategoryCreateView(CategoryFormMixin, CreateView):
    success_message = 'Category "{title}" created.'


class CategoryUpdateView(CategoryFormMixin, UpdateView):
    success_message = 'Category "{title}" updated.'


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'manager/category_confirm_delete.html'
    success_url = reverse_lazy('manager:categories')

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.success(self.request, f'Category "{title}" deleted.')
        return response
