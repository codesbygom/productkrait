from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from typing import Any, Dict
from ..repositories import CartRepository, ProductRepository
from ..models import Cart, CartItem, Order, OrderItem
from shop.models import Product
from .payment_views import go_to_gateway_view
from django.conf import settings
import json

class AddToCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            with transaction.atomic():
                cart = self.cart_repository.get_or_create_cart(request.user)
                quantity = int(request.POST.get('quantity', 1))
                
                if quantity <= 0:
                    messages.error(request, 'Quantity must be greater than zero.')
                    return redirect('shop:detail', id=product_id)

                # Lock the product to check quantity
                product = Product.objects.select_for_update().get(id=product_id)

                if quantity > product.quantity:
                    messages.error(request, 'Not enough stock available.')
                    return redirect('shop:detail', id=product_id)

                cart_item, created = self.cart_repository.add_item(cart, product, quantity)

                messages.success(request, 'Product added to cart')
                return redirect('shop:checkout')

        except Exception as e:
            messages.error(request, f'System error: {str(e)}')
            return redirect('shop:detail', id=product_id)

class UpdateCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                if self.cart_repository.remove_item(cart, product_id):
                    messages.success(request, 'Product removed from cart.')
                else:
                    messages.error(request, 'Error removing the product from the cart.')
                return redirect('shop:checkout')

            product = Product.objects.select_for_update().get(id=product_id)

            if quantity > product.quantity:
                messages.error(request, 'Not enough stock available.')
                return redirect('shop:checkout')

            cart_item = self.cart_repository.update_item_quantity(cart, product_id, quantity)
            if cart_item:
                messages.success(request, 'Cart updated.')
            else:
                messages.error(request, 'Error updating the cart.')

            return redirect('shop:checkout')

        except Exception as e:
            messages.error(request, f'System error: {str(e)}')
            return redirect('shop:checkout')

class RemoveFromCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            if self.cart_repository.remove_item(cart, product_id):
                messages.success(request, 'Product removed from cart')
            else:
                messages.error(request, 'Error removing the product from the cart.')
            return redirect('shop:checkout')

        except Exception as e:
            messages.error(request, f'System error: {str(e)}')
            return redirect('shop:checkout')

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/checkout.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def get_context_data(self, **kwargs):
        """Get cart items and total for checkout."""
        context = super().get_context_data(**kwargs)
        cart = self.cart_repository.get_active_cart(self.request.user)
        
        if cart and cart.items.exists():
            context['cart_items'] = cart.items.all()
            context['total'] = cart.total_price
            context['is_empty'] = False
        else:
            context['cart_items'] = []
            context['total'] = 0
            context['is_empty'] = True

        user = self.request.user
        context['shipping'] = {
            'full_name': user.get_full_name(),
            'phone': user.phone or '',
            'address': ', '.join(part for part in (user.address, user.city, str(user.zipcode or '')) if part),
        }
        context['minimum_order_amount'] = settings.MINIMUM_ORDER_AMOUNT
        return context

    def post(self, request, *args, **kwargs):
        cart = self.cart_repository.get_active_cart(request.user)
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('shop:checkout')

        address = request.POST.get('address', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        if not address or not full_name or not phone:
            messages.error(request, 'Please enter your name, phone number and shipping address.')
            return redirect('shop:checkout')
        if cart.total_price < settings.MINIMUM_ORDER_AMOUNT:
            messages.error(request, f'Your order total must be at least {settings.MINIMUM_ORDER_AMOUNT:,} Toman.')
            return redirect('shop:checkout')

        # the courier needs who and how to reach, not just where
        request.session['shipping_address'] = f'{full_name} ({phone})\n{address}'
        return go_to_gateway_view(request)

        


class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest order for the current user
        try:
            order = Order.objects.filter(user=self.request.user).latest('created_at')
            context['order'] = order
            context['order_items'] = order.items.all()
            context['status_display'] = dict(Order.STATUS_CHOICES)[order.status]
        except Order.DoesNotExist:
            context['order'] = None
            context['order_items'] = []
            context['status_display'] = None
        return context 


class FailureView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/failure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest payment for the current user
        try:
            from shop.models import Payment
            payment = Payment.objects.filter(user=self.request.user).latest('created_at')
            context['payment'] = payment
        except Payment.DoesNotExist:
            context['payment'] = None
        return context 