import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.http import HttpResponse, Http404
from shop.models import Cart, Order, OrderItem
from shop.models import Payment
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from shop.repositories import CartRepository

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

    # Use the data available on the bank record to create the corresponding
    # record or perform whatever action is appropriate.
    if bank_record.is_success:
        shipping_address = request.session.pop('shipping_address', '')
        if not shipping_address:
            messages.error(request, 'Please enter a shipping address.')
            return redirect('shop:checkout')

        new_payment = Payment()
        new_payment.user = current_user
        new_payment.payment_number = bank_record.tracking_code
        new_payment.payment_method = bank_record.bank_type
        new_payment.amount_paid = bank_record.amount
        new_payment.status = bank_record.status
        new_payment.save()
        # The payment was completed successfully and confirmed by the bank.
        # You can redirect the user to a result page or display the result.
        try:
            order = cart_repository.create_order(cart, shipping_address)
            order.payment = new_payment
            order.save()
            messages.success(request, 'Your order was placed successfully.')
            cart_repository.clear_cart(cart)
            return redirect('shop:success')
        except Exception as e:
            cart_repository.clear_cart(cart)
            messages.error(request, 'System error while placing the order. Please contact support.')
            return redirect('shop:failure')
    else:
        cart_repository.clear_cart(cart)
        messages.error(request, 'Payment failed. If an amount was deducted, it will be refunded within 48 hours.')
        return redirect('shop:failure')
