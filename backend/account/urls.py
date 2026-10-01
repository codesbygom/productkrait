from django.urls import path
from account.views import (
    RegisterView, ProfileView,
    OrderListView, OrderDetailView,
)
from account.views.auth_views import (
    CustomLoginView as LoginView, CustomLogoutView as LogoutView,
    CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
)

app_name = 'account'

urlpatterns = [
    # User authentication views
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/', CustomPasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/sent/', CustomPasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password-reset-complete'),

    # Order management URLs
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:order>/', OrderDetailView.as_view(), name='order-detail'),
]
