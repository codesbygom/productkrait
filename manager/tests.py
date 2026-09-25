from django.test import TestCase
from django.urls import reverse

from account.models import User
from shop.models import Order, Payment


class ManagerPanelTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user(email='staff@example.com', password='Str0ng-pass!', username='staff', is_staff=True)
        self.customer = User.objects.create_user(email='buyer@example.com', password='Str0ng-pass!', username='buyer')
        Order.objects.create(user=self.customer, total_price=250000, shipping_address='x', status='processing')
        Order.objects.create(user=self.customer, total_price=999, shipping_address='x', status='cancelled')
        Payment.objects.create(user=self.customer, payment_number='TRK-1', payment_method='online', amount_paid=250000, status='completed')

    def test_customers_are_kept_out(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('manager:customers'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('manager:login'), response.url)

    def test_dashboard_revenue_ignores_cancelled_orders(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('manager:dashboard'))
        self.assertEqual(response.context['revenue'], 250000)
        self.assertEqual(response.context['customer_count'], 1)

    def test_customer_list_search_and_detail(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('manager:customers'), {'q': 'buyer'})
        self.assertEqual([c.email for c in response.context['customers']], ['buyer@example.com'])
        detail = self.client.get(reverse('manager:customer-detail', args=[self.customer.pk]))
        self.assertEqual(detail.context['total_spent'], 250000)

    def test_block_and_unblock_customer(self):
        self.client.force_login(self.staff)
        url = reverse('manager:customer-toggle-active', args=[self.customer.pk])
        self.client.post(url)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)
        self.client.post(url)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)

    def test_staff_cannot_be_blocked(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('manager:customer-toggle-active', args=[self.staff.pk]))
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)

    def test_payment_list_filter(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('manager:payments'), {'status': 'failed'})
        self.assertEqual(len(response.context['payments']), 0)
        response = self.client.get(reverse('manager:payments'), {'q': 'TRK'})
        self.assertEqual(len(response.context['payments']), 1)
