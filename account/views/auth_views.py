from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from account.forms import UserRegistrationForm, UserUpdateForm, CustomPasswordChangeForm

class RegisterView(CreateView):
    template_name = 'Account/signup.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('account:profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        # sign the new customer straight in instead of bouncing them to the login page
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Welcome to ProductKrait! Your account has been created.')
        return response

class CustomLoginView(LoginView):
    template_name = 'Account/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('shop:index')

    def get_success_url(self):
        # honour ?next= (e.g. coming from "add to cart"), otherwise go to the shop
        return self.get_redirect_url() or str(self.success_url)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('shop:index')
    http_method_names = ['get', 'post']

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'Account/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('account:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been saved.')
        return super().form_valid(form)
