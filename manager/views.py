from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from shop.forms import CategoryForm, OrderUpdateForm, ProductForm
from account.models import User
from shop.models import Category, Order, OrderItem, Payment, Product

from .forms import StaffAuthenticationForm
from .mixins import StaffRequiredMixin

LOW_STOCK = 5
# orders that never turned into money
PENDING_OR_CANCELLED = ('pending', 'cancelled')


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
            customer_count=User.objects.filter(is_staff=False).count(),
            revenue=Order.objects.exclude(status__in=PENDING_OR_CANCELLED).aggregate(total=Sum('total_price'))['total'] or 0,
            recent_orders=Order.objects.select_related('user').order_by('-created_at')[:5],
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


class CustomerListView(StaffRequiredMixin, ListView):
    template_name = 'manager/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.annotate(order_count=Count('orders')).order_by('-date_joined')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(email__icontains=q) | Q(username__icontains=q) |
                           Q(first_name__icontains=q) | Q(last_name__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class CustomerDetailView(StaffRequiredMixin, DetailView):
    model = User
    template_name = 'manager/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['orders'] = self.object.orders.order_by('-created_at')
        ctx['payments'] = self.object.payments.order_by('-created_at')
        ctx['total_spent'] = self.object.orders.exclude(status__in=PENDING_OR_CANCELLED).aggregate(
            total=Sum('total_price'))['total'] or 0
        return ctx


class CustomerToggleActiveView(StaffRequiredMixin, View):
    """Blocks / unblocks a customer's login. Staff accounts are left alone so
    nobody can lock the management team (or themselves) out from here."""
    http_method_names = ['post']

    def post(self, request, pk):
        customer = get_object_or_404(User, pk=pk)
        if customer.is_staff or customer.is_superuser:
            messages.error(request, 'Staff accounts cannot be blocked from the manager panel.')
        else:
            customer.is_active = not customer.is_active
            customer.save(update_fields=['is_active'])
            state = 'unblocked' if customer.is_active else 'blocked'
            messages.success(request, f'{customer.email} {state}.')
        return redirect('manager:customer-detail', pk=pk)
