import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from account.models import User
from shop.models import CartItem, Order, Product
from shop.repositories import CartRepository


MEDIA_ROOT = tempfile.mkdtemp()


def make_image():
    buffer = BytesIO()
    Image.new('RGB', (20, 20), 'green').save(buffer, 'PNG')
    return SimpleUploadedFile('p.png', buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CheckoutTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com', password='Str0ng-pass!', username='buyer',
            first_name='Sara', last_name='K', phone=9121234567, city='Tehran', address='Street 1')
        self.client.force_login(self.user)

    def fill_cart(self, price):
        product = Product.objects.create(title='Thing', slug='thing', price=price, quantity=5, image=make_image())
        cart = CartRepository().get_or_create_cart(self.user)
        CartItem.objects.create(cart=cart, product=product, quantity=1, price=price)

    def test_checkout_prefills_shipping_from_profile(self):
        self.fill_cart(200000)
        response = self.client.get(reverse('shop:checkout'))
        self.assertContains(response, 'value="Sara K"')
        self.assertContains(response, 'Street 1, Tehran')

    def test_empty_cart_cannot_check_out(self):
        response = self.client.post(reverse('shop:checkout'), {'full_name': 'x', 'phone': '1', 'address': 'y'}, follow=True)
        self.assertContains(response, 'Your cart is empty.')

    @override_settings(MINIMUM_ORDER_AMOUNT=100000)
    def test_minimum_order_message_uses_the_setting(self):
        self.fill_cart(500)
        response = self.client.post(reverse('shop:checkout'), {'full_name': 'x', 'phone': '1', 'address': 'y'}, follow=True)
        self.assertContains(response, 'at least 100,000 Toman')


@override_settings(MEDIA_ROOT=MEDIA_ROOT, PAYMENT_BACKEND='mock', MINIMUM_ORDER_AMOUNT=1000)
class MockPaymentTests(CheckoutTests):

    def start(self):
        self.fill_cart(200000)
        return self.client.post(reverse('shop:checkout'), {'full_name': 'Sara', 'phone': '912', 'address': 'Street 1'})

    def test_checkout_redirects_to_mock_bank(self):
        self.assertRedirects(self.start(), reverse('mock-payment'))
        self.assertContains(self.client.get(reverse('mock-payment')), '200,000')

    def test_paying_places_the_order_once(self):
        self.start()
        response = self.client.post(reverse('mock-payment-result'), {'result': 'success'})
        self.assertRedirects(response, reverse('shop:success'))
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        # the pending payment is consumed, so replaying the POST can't double-charge
        self.assertEqual(self.client.post(reverse('mock-payment-result'), {'result': 'success'}).status_code, 404)

    def test_failing_keeps_the_cart_and_places_no_order(self):
        self.start()
        response = self.client.post(reverse('mock-payment-result'), {'result': 'fail'})
        self.assertRedirects(response, reverse('shop:failure'))
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_mock_bank_needs_a_pending_payment(self):
        self.assertEqual(self.client.get(reverse('mock-payment')).status_code, 404)


class CatalogCacheTests(TestCase):

    def test_category_menu_cache_is_invalidated_on_change(self):
        from shop.cache import get_category_tree
        from shop.models import Category
        Category.objects.create(title='Phones', slug='phones', position=1)
        self.assertEqual([c.slug for c in get_category_tree()], ['phones'])
        with self.assertNumQueries(0):
            get_category_tree()  # served from the cache
        Category.objects.create(title='Laptops', slug='laptops', position=2)
        self.assertEqual(sorted(c.slug for c in get_category_tree()), ['laptops', 'phones'])
