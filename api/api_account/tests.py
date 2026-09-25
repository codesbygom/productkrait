import re

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

from account.models import User, EmailOTP


class AccountAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='arash@example.com', password='Str0ng-pass!', username='arash')

    def test_register_hashes_password_sends_mail(self):
        response = self.client.post(reverse('api-register'), {
            'email': 'new@example.com', 'username': 'new', 'password': 'An0ther-pass!'})
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data['data'])
        user = User.objects.get(email='new@example.com')
        self.assertTrue(user.check_password('An0ther-pass!'))
        self.assertFalse(user.is_email_verified)
        self.assertEqual(len(mail.outbox), 1)

    def test_register_cannot_self_verify(self):
        self.client.post(reverse('api-register'), {
            'email': 'sneaky@example.com', 'username': 'sneaky', 'password': 'An0ther-pass!', 'is_email_verified': True})
        self.assertFalse(User.objects.get(email='sneaky@example.com').is_email_verified)

    def test_register_rejects_weak_password(self):
        response = self.client.post(reverse('api-register'), {'email': 'w@example.com', 'username': 'w', 'password': '123'})
        self.assertEqual(response.status_code, 400)

    def test_verify_email_link(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(reverse('api-request-verification')).status_code, 202)
        token = EmailOTP.objects.get(user=self.user).email_verification_code
        self.assertIn(token, mail.outbox[0].body)

        self.client.force_authenticate(None)
        response = self.client.get(reverse('api-verify-email', args=[token]))
        self.assertEqual(response.status_code, 202)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_jwt_login_and_logout(self):
        response = self.client.post(reverse('api-token-obtain'), {'email': 'arash@example.com', 'password': 'Str0ng-pass!'})
        self.assertEqual(response.status_code, 200)
        refresh = response.data['refresh']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        self.assertEqual(self.client.post(reverse('api-logout'), {'refresh': refresh}).status_code, 205)
        again = self.client.post(reverse('api-token-refresh'), {'refresh': refresh})
        self.assertEqual(again.status_code, 401)

    def test_profile_get_and_update(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(reverse('api-profile')).data['email'], 'arash@example.com')
        response = self.client.patch(reverse('api-profile'), {'city': 'Tehran', 'zipcode': 12345})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, 'Tehran')

    def test_change_password(self):
        self.client.force_authenticate(self.user)
        url = reverse('api-change-password')
        wrong = self.client.put(url, {'old_password': 'nope', 'new_password': 'N3w-pass-ok!', 'confirmed_password': 'N3w-pass-ok!'})
        self.assertEqual(wrong.status_code, 400)
        ok = self.client.put(url, {'old_password': 'Str0ng-pass!', 'new_password': 'N3w-pass-ok!', 'confirmed_password': 'N3w-pass-ok!'})
        self.assertEqual(ok.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w-pass-ok!'))

    def test_forget_and_reset_password(self):
        response = self.client.post(reverse('api-forget-password'), {'email': 'arash@example.com'})
        self.assertEqual(response.status_code, 200)
        link = re.search(r'/api/account/reset-password/[^\s?]+', mail.outbox[0].body).group(0)

        response = self.client.put(link, {'new_password': 'Reset-pass-9!', 'confirmed_password': 'Reset-pass-9!'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Reset-pass-9!'))
        # the token is single-use: the password (and so the token hash) changed
        self.assertEqual(self.client.put(link, {'new_password': 'Other-pass-9!', 'confirmed_password': 'Other-pass-9!'}).status_code, 400)

    def test_forget_password_does_not_reveal_unknown_email(self):
        response = self.client.post(reverse('api-forget-password'), {'email': 'nobody@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
