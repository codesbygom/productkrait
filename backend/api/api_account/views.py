from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from account.models import User, EmailOTP
from .serializers import *
from .utils import send_email, issue_email_verification


class Logout(GenericAPIView):
    """Blacklists the given refresh token so it can't mint new access tokens."""
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data['refresh']).blacklist()
        except TokenError:
            return Response({'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class Register(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        issue_email_verification(request, user, request.data.get('redirect_url', ''))

        return Response({
            'message': 'registered succesfully check email',
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)


@api_view(["POST",])
@permission_classes([IsAuthenticated])
def request_email_verification(request):
    user = request.user
    if user.is_email_verified:
        return Response({'message': 'your email was verified'}, status=status.HTTP_400_BAD_REQUEST)

    issue_email_verification(request, user, request.data.get('redirect_url', ''))
    return Response({'message': 'email was sent to your email address'}, status=status.HTTP_202_ACCEPTED)


# GET so the link in the mail works when clicked straight from the inbox.
@api_view(["GET", "POST",])
@permission_classes([AllowAny])
def verify_email(request,token):
    try:
        email_otp = EmailOTP.objects.select_related('user').get(email_verification_code=token)
    except EmailOTP.DoesNotExist:
        return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    if email_otp.user.is_email_verified:
        return Response({'message': 'your email is already verified'}, status=status.HTTP_400_BAD_REQUEST)

    if email_otp.is_expired():
        return Response({'message': 'expired OTP try getting a new OTP'}, status=status.HTTP_400_BAD_REQUEST)

    user = email_otp.user
    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])
    email_otp.delete()
    return Response({'message': 'email verified succesfully'}, status=status.HTTP_202_ACCEPTED)


class ForgetPassword(GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data['email']).first()

        if user is not None:
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            absurl = request.build_absolute_uri(
                reverse('api-reset-password', kwargs={'uidb64': uidb64, 'token': token}))

            redirect_url = serializer.validated_data['redirect_url']
            if redirect_url:
                absurl += '?redirect_url=' + redirect_url
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
            send_email({'email_body': email_body, 'to_emails': [user.email],
                'email_subject': 'Reset your passsword'})

        # Same answer either way, so this can't be used to probe which emails are registered.
        return Response({'success': 'If that email is registered, we have sent you a link to reset your password'},
                        status=status.HTTP_200_OK)


class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def put(self, request, uidb64, token):
        try:
            user = User.objects.get(id=smart_str(urlsafe_base64_decode(uidb64)))
        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            return Response({'failed': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'failed': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password updated successfully'})

    patch = put


class ChangePassword(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "password updated successfully"})


class UpdateProfile(RetrieveUpdateAPIView):
    serializer_class=UpdateProfileSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
