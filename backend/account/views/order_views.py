from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from shop.models import Order, OrderItem


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'Account/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'Account/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        return get_object_or_404(Order, id=self.kwargs['order'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_details'] = OrderItem.objects.filter(order=self.object)
        return context
