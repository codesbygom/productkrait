from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from .. import services
from ..services import CartError
from ..models import Order, Payment
from .payment_views import go_to_gateway_view
import logging

logger = logging.getLogger(__name__)


def _quantity(request, default):
    try:
        return int(request.POST.get('quantity', default))
    except ValueError:
        raise CartError('Invalid quantity.')


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            services.add_to_cart(request.user, product_id, _quantity(request, 1))
        except CartError as e:
            messages.error(request, str(e))
            return redirect('shop:detail', id=product_id)
        except Exception:
            logger.exception("Cart operation failed")  # details to logs, not to the user
            messages.error(request, 'System error. Please try again.')
            return redirect('shop:detail', id=product_id)

        messages.success(request, 'Product added to cart')
        return redirect('shop:checkout')


class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            quantity = _quantity(request, 0)
            if quantity <= 0:
                if services.remove_from_cart(request.user, product_id):
                    messages.success(request, 'Product removed from cart.')
                else:
                    messages.error(request, 'Error removing the product from the cart.')
            else:
                services.update_cart_item(request.user, product_id, quantity)
                messages.success(request, 'Cart updated.')
        except CartError as e:
            messages.error(request, str(e))
        except Exception:
            logger.exception("Cart update failed")
            messages.error(request, 'System error. Please try again.')
        return redirect('shop:checkout')


class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        if services.remove_from_cart(request.user, product_id):
            messages.success(request, 'Product removed from cart')
        else:
            messages.error(request, 'Error removing the product from the cart.')
        return redirect('shop:checkout')


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/checkout.html'

    def get_context_data(self, **kwargs):
        """Get cart items and total for checkout."""
        context = super().get_context_data(**kwargs)
        cart = services.get_active_cart(self.request.user)

        if cart and cart.items.exists():
            context['cart_items'] = cart.items.select_related('product')
            context['total'] = cart.total_price
            context['is_empty'] = False
        else:
            context['cart_items'] = []
            context['total'] = 0
            context['is_empty'] = True

        return context

    def post(self, request, *args, **kwargs):
        cart = services.get_active_cart(request.user)
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('shop:checkout')

        shipping_address = request.POST.get('address', '').strip()
        if not shipping_address:
            messages.error(request, 'Please enter a shipping address.')
            return redirect('shop:checkout')
        if cart.total_price < settings.MINIMUM_ORDER_AMOUNT:
            messages.error(request, 'Your order total must be greater than 1000 Toman.')
            return redirect('shop:checkout')

        request.session['shipping_address'] = shipping_address
        return go_to_gateway_view(request)


class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest order for the current user
        order = Order.objects.filter(user=self.request.user).order_by('-created_at').first()
        context['order'] = order
        context['order_items'] = order.items.all() if order else []
        context['status_display'] = order.get_status_display() if order else None
        return context


class FailureView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/failure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest payment for the current user
        context['payment'] = Payment.objects.filter(user=self.request.user).order_by('-created_at').first()
        return context
