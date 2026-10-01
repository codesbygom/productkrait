from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .auth_views import (
    RegisterView,
    CustomLoginView as LoginView,
    CustomLogoutView as LogoutView,
    ProfileView
)
from .order_views import (
    OrderListView,
    OrderDetailView,
)

__all__ = [
    # Auth views
    'RegisterView',
    'LoginView',
    'LogoutView',
    'ProfileView',
    # Order views
    'OrderListView',
    'OrderDetailView',
] 