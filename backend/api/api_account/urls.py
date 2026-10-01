from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *


urlpatterns = [
    path('register/', Register.as_view(), name='api-register'),
    path('token/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='api-token-verify'),
    path('logout/', Logout.as_view(), name='api-logout'),
    path('profile/', UpdateProfile.as_view(), name='api-profile'),
    path('verify-email/<str:token>/', verify_email, name='api-verify-email'),
    path('request-verification/',request_email_verification, name="api-request-verification"),
    path('forget-password/', ForgetPassword.as_view(), name='api-forget-password'),
    path('reset-password/<uidb64>/<token>/', ResetPassword.as_view(), name='api-reset-password'),
    path('change-password/', ChangePassword.as_view(), name='api-change-password')
]
