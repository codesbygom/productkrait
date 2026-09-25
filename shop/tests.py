import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from account.models import User
from shop.models import CartItem, Product
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
