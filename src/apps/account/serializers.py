from rest_framework import serializers
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

from . import models, exceptions
from .enums import UserRoleEnum


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class AccessTokenSerializer(serializers.Serializer):
    access = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user_role = serializers.CharField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[EmailValidator()])


class LoginOTPSerializer(EmailSerializer, serializers.Serializer):
    code = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):

    referral = serializers.CharField(max_length=8, required=False)
    otp_code = serializers.CharField()

    class Meta:
        model = models.User
        fields = (
            'email', 'first_name', 'last_name', 'role',
            'otp_code', 'referral'
        )

    def validate_email(self, value):
        if models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("A user with this email has already registered.")
            )
        return value

    def create(self, validated_data):
        validated_data = validated_data.copy()
        validated_data.pop('otp_code', None)
        validated_data.pop('referral', None)

        user = self.Meta.model(**validated_data)

        password = validated_data.get('password')
        if password:
            user.set_password(password)
        else:
            raise ValueError(_('Password is required'))

        user.save()
        return user


class ConfirmEmailSerializer(serializers.Serializer):
    code = serializers.CharField()


class ResetPasswordCheckSetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    code = serializers.CharField()
    password = serializers.CharField()
