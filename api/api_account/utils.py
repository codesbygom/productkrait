from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from account.models import EmailOTP


def send_email(data):
    email = EmailMessage(
        data['email_subject'],
        data['email_body'] ,
        settings.DEFAULT_FROM_EMAIL,
        data['to_emails'],
    )
    email.send()

def get_unique_code():
    return get_random_string(64)


def issue_email_verification(request, user, redirect_url=''):
    """Creates (or refreshes) the user's verification code and mails them the link."""
    email_otp, _ = EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            'email_verification_code': get_unique_code(),
            'expiration_date': timezone.now() + timezone.timedelta(days=7),
        },
    )

    absurl = request.build_absolute_uri(reverse('api-verify-email', kwargs={'token': email_otp.email_verification_code}))
    if redirect_url:
        absurl += '?redirect_url=' + redirect_url
    send_email({
        'email_body': 'Hello, \n Use link below to verify your email  \n' + absurl,
        'to_emails': [user.email],
        'email_subject': 'Verify your email',
    })
    return email_otp
