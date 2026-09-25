import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.http import HttpResponse, Http404
from shop.models import Cart, Order, OrderItem
from shop.models import Payment
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from shop.repositories import CartRepository

@login_required
def go_to_gateway_view(request):

    # Read the amount from wherever is relevant
    cart_repository = CartRepository()
    cart = cart_repository.get_active_cart(request.user)
    total_price = cart.total_price

    factory = bankfactories.BankFactory()
    try:
        bank = (factory.auto_create()) # or factory.create(bank_models.BankType.BMI) or set identifier
        bank.set_request(request)
        bank.set_amount(total_price)
        # Callback URL for the app to continue the process
        bank.set_client_callback_url(reverse("call-back-gateway"))
        # Optionally link this record to an invoice or anything else you might
        # need to connect the product/service to this payment later.
        bank_record = bank.ready()
        # Redirect the user to the bank gateway
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        # cart_repository.clear_cart(cart)
        messages.error(request, 'System error while redirecting to the bank gateway...')
        return redirect('shop:checkout')

@login_required
def callback_gateway_view(request):

    current_user = request.user
    cart_repository = CartRepository()
    cart = cart_repository.get_active_cart(request.user)


    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("This link is not valid.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("This link is not valid.")
        raise Http404

    # Reloading the callback page must not record the payment (or the order) twice.
    if Payment.objects.filter(payment_number=bank_record.tracking_code, user=current_user).exists():
        return redirect('shop:success' if bank_record.is_success else 'shop:failure')

    Payment.objects.create(
        user=current_user,
        payment_number=bank_record.tracking_code,
        payment_method='online',
        amount_paid=bank_record.amount if bank_record.is_success else 0,
        status='completed' if bank_record.is_success else 'failed',
    )

    if not bank_record.is_success:
        # The cart is kept so the customer can simply try paying again.
        messages.error(request, 'Payment failed. If an amount was deducted, it will be refunded within 48 hours.')
        return redirect('shop:failure')

    # The payment was completed successfully and confirmed by the bank.
    payment = Payment.objects.get(payment_number=bank_record.tracking_code, user=current_user)
    shipping_address = request.session.pop('shipping_address', '') or current_user.address or ''
    try:
        if cart is None:
            raise ValueError('No active cart')
        order = cart_repository.create_order(cart, shipping_address)
        order.payment = payment
        order.save()
        messages.success(request, 'Your order was placed successfully.')
        return redirect('shop:success')
    except Exception:
        logging.exception('Could not create the order for paid tracking code %s', bank_record.tracking_code)
        messages.error(request, 'Your payment was received but we could not place the order. '
                                'Please contact support with tracking code %s.' % bank_record.tracking_code)
        return redirect('shop:failure')
