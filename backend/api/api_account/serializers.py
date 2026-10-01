from rest_framework import serializers
from account.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'is_email_verified', ]
        read_only_fields = ['id', 'is_email_verified']

    def validate(self, data):
        validate_password(data['password'], User(email=data.get('email'), username=data.get('username')))
        return data

    def create(self, validated_data):
        """ Creates and returns a new user """
        return User.objects.create_user(**validated_data)


class ResetPasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(required=True, write_only=True)
    confirmed_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError({'confirmed_password': 'passwords should match'})
        validate_password(data['new_password'], self.context.get('user'))
        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirmed_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({'old_password': 'Wrong password.'})
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({'new_password': 'new password should not match with old password'})
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        validate_password(data['new_password'], user)
        return data


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    redirect_url = serializers.CharField(required=False, allow_blank=True, default='')


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'zipcode', 'address', 'city', 'phone', 'is_email_verified', ]
        read_only_fields = ['id', 'is_email_verified']

    def update(self, instance, validated_data):
        # A new address has to be verified again.
        if 'email' in validated_data and validated_data['email'] != instance.email:
            instance.is_email_verified = False
        return super().update(instance, validated_data)
