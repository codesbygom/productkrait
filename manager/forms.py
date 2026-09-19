from django import forms
from django.contrib.auth.forms import AuthenticationForm


class StaffAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'not_staff': 'This account does not have access to the management area.',
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(self.error_messages['not_staff'], code='not_staff')
