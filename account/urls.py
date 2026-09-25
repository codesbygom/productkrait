from django.urls import path
from account.views import (
    RegisterView, ProfileView,
    OrderListView, OrderDetailView,
)
from account.views.auth_views import (
    CustomLoginView as LoginView, CustomLogoutView as LogoutView,
    CustomPasswordChangeView,
)

app_name = 'account'

urlpatterns = [
    # User authentication views
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/', CustomPasswordChangeView.as_view(), name='password-change'),

    # Order management URLs
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:order>/', OrderDetailView.as_view(), name='order-detail'),
]
