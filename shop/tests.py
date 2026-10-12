from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from account.models import User
from . import services
from .models import Cart, Category, Product
from .services import CartError


def make_product(title, category=None, quantity=10, price='1000'):
    product = Product.objects.create(
        title=title, slug=title.lower(), price=Decimal(price),
        quantity=quantity, image='products/test.jpg',
    )
    if category:
        product.category.add(category)
    return product


class QuerySetTests(TestCase):
    def test_in_category_includes_descendants_once(self):
        parent = Category.objects.create(title='Parent', slug='parent', position=1)
        child = Category.objects.create(title='Child', slug='child', position=2, parent=parent)
        in_parent = make_product('A', parent)
        in_child = make_product('B', child)
        in_child.category.add(parent)  # in both: must still appear once
        make_product('C')

        self.assertEqual(
            list(Product.objects.in_category(parent).order_by('title')),
            [in_parent, in_child],
        )

    def test_search_is_case_insensitive(self):
        phone = make_product('Phone')
        make_product('Laptop')
        self.assertEqual(list(Product.objects.search('phO')), [phone])


class ProductViewTests(TestCase):
    def test_second_page_lists_remaining_products(self):
        for i in range(10):
            make_product(f'P{i}')
        response = self.client.get(reverse('shop:index'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['product_obj']), 2)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_missing_product_is_404(self):
        response = self.client.get(reverse('shop:detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_inactive_category_is_404(self):
        Category.objects.create(title='Hidden', slug='hidden', position=1, status=False)
        response = self.client.get(reverse('shop:category', args=['hidden']))
        self.assertEqual(response.status_code, 404)

    def test_search_page(self):
        make_product('Phone')
        response = self.client.get(reverse('shop:search'), {'q': 'pho'})
        self.assertContains(response, 'Phone')


class CartServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='u@example.com', password='pass12345')
        self.product = make_product('Phone', quantity=5)

    def test_add_twice_increments_quantity(self):
        services.add_to_cart(self.user, self.product.id, 2)
        item = services.add_to_cart(self.user, self.product.id, 1)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(Cart.objects.active().filter(user=self.user).count(), 1)

    def test_add_more_than_stock_fails(self):
        with self.assertRaises(CartError):
            services.add_to_cart(self.user, self.product.id, 6)

    def test_update_and_remove(self):
        services.add_to_cart(self.user, self.product.id, 1)
        services.update_cart_item(self.user, self.product.id, 4)
        cart = services.get_active_cart(self.user)
        self.assertEqual(cart.items.get().quantity, 4)

        self.assertTrue(services.remove_from_cart(self.user, self.product.id))
        self.assertFalse(services.remove_from_cart(self.user, self.product.id))

    def test_update_item_not_in_cart_fails(self):
        with self.assertRaises(CartError):
            services.update_cart_item(self.user, self.product.id, 1)

    def test_create_order_takes_stock_and_closes_cart(self):
        services.add_to_cart(self.user, self.product.id, 2)
        cart = services.get_active_cart(self.user)

        order = services.create_order_from_cart(cart, 'Tehran')

        self.assertEqual(order.total_price, Decimal('2000'))
        self.assertEqual(order.items.get().quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)
        self.assertIsNone(services.get_active_cart(self.user))


class CartViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='u@example.com', password='pass12345')
        self.product = make_product('Phone', quantity=5)
        self.client.force_login(self.user)

    def test_add_to_cart_redirects_to_checkout(self):
        response = self.client.post(reverse('shop:add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertRedirects(response, reverse('shop:checkout'))
        self.assertEqual(services.get_active_cart(self.user).total_items, 2)

    def test_invalid_quantity_does_not_crash(self):
        response = self.client.post(reverse('shop:add_to_cart', args=[self.product.id]), {'quantity': 'abc'})
        self.assertRedirects(response, reverse('shop:detail', args=[self.product.id]))

    def test_update_to_zero_removes_item(self):
        services.add_to_cart(self.user, self.product.id, 2)
        self.client.post(reverse('shop:update_cart', args=[self.product.id]), {'quantity': 0})
        self.assertFalse(services.get_active_cart(self.user).items.exists())
