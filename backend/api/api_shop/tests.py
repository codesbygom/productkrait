import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from account.models import User
from shop.models import Category, Order, OrderItem, Product


MEDIA_ROOT = tempfile.mkdtemp()


def make_image(name='p.png'):
    buffer = BytesIO()
    Image.new('RGB', (20, 20), 'blue').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ShopAPITests(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(email='buyer@example.com', password='Str0ng-pass!', username='buyer')
        self.staff = User.objects.create_user(email='staff@example.com', password='Str0ng-pass!', username='staff', is_staff=True)
        self.category = Category.objects.create(title='Phones', slug='phones', position=1)
        self.hidden = Category.objects.create(title='Hidden', slug='hidden', position=2, status=False)
        self.product = Product.objects.create(title='Snake phone', slug='snake-phone', price=100, quantity=3, image=make_image())
        self.product.category.add(self.category)

    # --- catalogue -------------------------------------------------------

    def test_product_list_filters(self):
        url = reverse('api-product-list')
        self.assertEqual(self.client.get(url).data['count'], 1)
        self.assertEqual(self.client.get(url, {'category': 'phones'}).data['count'], 1)
        self.assertEqual(self.client.get(url, {'search': 'nothing-like-this'}).data['count'], 0)

    def test_legacy_endpoints_still_work(self):
        self.assertEqual(len(self.client.get(reverse('api-latest-products')).data), 1)
        self.assertEqual(self.client.get('/api/shop/phones/snake-phone/').data['id'], self.product.id)
        self.assertEqual(len(self.client.post(reverse('api-search'), {'query': 'snake'}).data), 1)
        self.assertEqual(len(self.client.get(reverse('api-search'), {'query': 'snake'}).data), 1)

    def test_hidden_categories_only_for_staff(self):
        url = reverse('api-category-list')
        self.assertEqual([c['slug'] for c in self.client.get(url).data], ['phones'])
        self.assertEqual(self.client.get('/api/shop/hidden/').status_code, 404)
        self.client.force_authenticate(self.staff)
        self.assertEqual(len(self.client.get(url).data), 2)

    def test_only_staff_can_write_products(self):
        payload = {'title': 'New', 'slug': 'new', 'price': '10.00', 'quantity': 1, 'category': ['phones'], 'image': make_image()}
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(reverse('api-product-list'), payload, format='multipart').status_code, 403)
        self.client.force_authenticate(self.staff)
        payload['image'] = make_image()
        response = self.client.post(reverse('api-product-list'), payload, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)

    def test_discount_cannot_exceed_price(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(reverse('api-product-detail', args=[self.product.id]), {'discount_price': '500'})
        self.assertEqual(response.status_code, 400)

    # --- cart ------------------------------------------------------------

    def test_cart_requires_auth(self):
        self.assertEqual(self.client.get(reverse('api-cart')).status_code, 401)

    def test_cart_flow(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('api-cart-items'), {'product_id': self.product.id, 'quantity': 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['total_items'], 2)

        # 2 in the cart + 2 more would exceed the 3 in stock
        over = self.client.post(reverse('api-cart-items'), {'product_id': self.product.id, 'quantity': 2})
        self.assertEqual(over.status_code, 400)

        item_url = reverse('api-cart-item', args=[self.product.id])
        self.assertEqual(self.client.patch(item_url, {'quantity': 3}).data['total_items'], 3)
        self.assertEqual(self.client.patch(item_url, {'quantity': 9}).status_code, 400)
        self.assertEqual(self.client.delete(item_url).data['total_items'], 0)
        self.assertEqual(self.client.delete(item_url).status_code, 404)

    # --- orders ----------------------------------------------------------

    def test_orders_are_private(self):
        order = Order.objects.create(user=self.user, total_price=100, shipping_address='somewhere')
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price=100)

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('api-order-list'))
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['items'][0]['product']['id'], self.product.id)

        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(reverse('api-order-detail', args=[order.id])).status_code, 404)
