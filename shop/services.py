"""Cart and order business logic.

Reads live on the model QuerySets (Product.objects.search(), ...); anything
that changes several rows together or needs locking lives here, so views stay
thin and the rules are in one place.
"""
from django.db import transaction
from django.db.models import F

from .models import Cart, CartItem, Order, OrderItem, Product


class CartError(ValueError):
    """A cart rule was broken; the message is safe to show to the user."""


def get_active_cart(user):
    return Cart.objects.active().filter(user=user).first()


@transaction.atomic
def add_to_cart(user, product_id, quantity):
    if quantity <= 0:
        raise CartError('Quantity must be greater than zero.')

    # Lock the product so the stock check can't race another request
    product = Product.objects.select_for_update().get(pk=product_id)
    if quantity > product.quantity:
        raise CartError('Not enough stock available.')

    cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity, 'price': product.price},
    )
    if not created:
        # F(): increment in the DB, not read-modify-write in Python
        CartItem.objects.filter(pk=cart_item.pk).update(quantity=F('quantity') + quantity)
        cart_item.refresh_from_db(fields=['quantity'])
    return cart_item


@transaction.atomic
def update_cart_item(user, product_id, quantity):
    if quantity <= 0:
        raise CartError('Quantity must be greater than zero.')

    product = Product.objects.select_for_update().get(pk=product_id)
    if quantity > product.quantity:
        raise CartError('Not enough stock available.')

    updated = CartItem.objects.filter(
        cart__user=user, cart__is_active=True, product=product,
    ).update(quantity=quantity)
    if not updated:
        raise CartError('Error updating the cart.')


def remove_from_cart(user, product_id):
    deleted, _ = CartItem.objects.filter(
        cart__user=user, cart__is_active=True, product_id=product_id,
    ).delete()
    return deleted > 0


def create_order_from_cart(cart, shipping_address):
    """Turn the cart into an order, take the stock and close the cart."""
    with transaction.atomic():
        # Lock the cart to prevent concurrent modifications
        cart = Cart.objects.select_for_update().get(pk=cart.pk)
        if not cart.is_active or not cart.items.exists():
            raise CartError('Cart is empty or inactive')

        items = list(cart.items.select_related('product'))
        # Lock all products in one query, in a stable order (avoids deadlocks)
        products = {
            p.id: p for p in Product.objects.select_for_update()
            .filter(id__in=[i.product_id for i in items]).order_by('id')
        }
        for item in items:
            product = products[item.product_id]
            if product.quantity < item.quantity:
                raise CartError(f'Insufficient quantity for product: {product.title}')

        order = Order.objects.create(
            user=cart.user,
            total_price=cart.total_price,
            status='processing',
            shipping_address=shipping_address,
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product_id=item.product_id, quantity=item.quantity, price=item.price)
            for item in items
        ])
        for item in items:
            Product.objects.filter(id=item.product_id).update(quantity=F('quantity') - item.quantity)

        cart.clear()
        cart.is_active = False
        cart.save()
        return order
