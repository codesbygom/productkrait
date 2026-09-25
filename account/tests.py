import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from account.models import User


class AccountWebTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='arash@example.com', password='Str0ng-pass!', username='arash')

    def test_signup_logs_the_user_in(self):
        response = self.client.post(reverse('account:signup'), {
            'username': 'new', 'email': 'new@example.com',
            'password1': 'An0ther-pass!', 'password2': 'An0ther-pass!'})
        self.assertRedirects(response, reverse('account:profile'))
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(email='new@example.com').pk)

    def test_login_honours_next(self):
        response = self.client.post(reverse('account:login') + '?next=/account/orders/',
                                    {'username': 'arash@example.com', 'password': 'Str0ng-pass!'})
        self.assertRedirects(response, '/account/orders/')

    def test_profile_saves_shipping_details(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('account:profile'), {
            'first_name': 'Arash', 'last_name': 'G', 'email': 'arash@example.com',
            'phone': '9121234567', 'city': 'Tehran', 'zipcode': '12345', 'address': 'Street 1'})
        self.assertRedirects(response, reverse('account:profile'))
        self.user.refresh_from_db()
        self.assertEqual((self.user.city, self.user.address), ('Tehran', 'Street 1'))

    def test_password_change(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('account:password-change'), {
            'old_password': 'Str0ng-pass!', 'new_password1': 'N3w-pass-ok!', 'new_password2': 'N3w-pass-ok!'})
        self.assertRedirects(response, reverse('account:profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w-pass-ok!'))

    def test_password_reset_flow(self):
        response = self.client.post(reverse('account:password-reset'), {'email': 'arash@example.com'})
        self.assertRedirects(response, reverse('account:password-reset-done'))
        link = re.search(r'/account/password-reset/[^/\s]+/[^/\s]+/', mail.outbox[0].body).group(0)

        # Django swaps the token for a session marker and redirects to ".../set-password/"
        response = self.client.get(link, follow=True)
        self.assertTrue(response.context['validlink'])
        response = self.client.post(response.redirect_chain[-1][0], {
            'new_password1': 'Reset-pass-9!', 'new_password2': 'Reset-pass-9!'})
        self.assertRedirects(response, reverse('account:password-reset-complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Reset-pass-9!'))
