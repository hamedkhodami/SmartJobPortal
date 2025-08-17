from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions as base_permissions
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView as _TokenObtainPairView,
    TokenRefreshView as _TokenRefreshView,
)

from drf_yasg.utils import swagger_auto_schema

from apps.core.swagger import mixins as ms
from apps.core import utils, redis_utils

from .. import serializers, models, exceptions


User = get_user_model()


# ---Api Views---------------------------------------------------
class TokenRefresh(ms.SwaggerViewMixin, _TokenRefreshView):
    """
        get access token by refresh token(update login)
    """
    swagger_title = 'Token refresh'
    swagger_tags = ['Account']
    serializer_response = serializers.AccessTokenSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        return super(TokenRefresh, self).post(request, *args, **kwargs)


class LoginBasic(ms.SwaggerViewMixin, _TokenObtainPairView):
    """
        Get token pair (access & refresh tokens)
    """
    swagger_title = 'Login basic by raw password'
    swagger_tags = ['Account']
    serializer_response = serializers.TokenResponseSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        resp = super(LoginBasic, self).post(request, *args, **kwargs)

        email = request.data.get('email')
        try:
            user = get_user_model().objects.get(email=email)
            resp.data['user_role'] = user.role
        except get_user_model().DoesNotExist:
            resp.data['user_role'] = None

        return resp


class LoginOTP(APIView):
    """View to handle OTP-based authentication"""

    permission_classes = (base_permissions.AllowAny,)

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Login OTP: Send Code',
        security=[],
        query_serializer=serializers.EmailSerializer,
        responses={200: serializers.MessageSerializer}
    )
    def get(self, request):
        """Handles OTP code generation & sending"""
        ser = serializers.EmailSerializer(data=request.GET)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise exceptions.UserNotFound()

        conf = settings.LOGIN_OTP_CONFIG
        user_key = conf['STORE_BY'].format(email)

        if redis_utils.get_value(user_key):
            raise exceptions.CodeHasAlreadyBeenSent()

        otp_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, otp_code, conf['TIMEOUT'])

        # TODO: notification

        res = {'message': _('OTP code sent')}
        return Response(serializers.MessageSerializer(res).data)

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Login OTP: Verify Code & Get Tokens',
        request_body=serializers.LoginOTPSerializer,
        operation_description='Get token pair (access & refresh tokens)',
        security=[],
        responses={200: serializers.TokenResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        """Handles OTP verification & token retrieval"""
        ser = serializers.LoginOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data['email']
        user_code = ser.validated_data['code']

        try:
            user = User.objects.get(email=email, is_active=True)
        except ObjectDoesNotExist:
            raise exceptions.UserNotFound()

        conf = settings.LOGIN_OTP_CONFIG
        user_key = conf['STORE_BY'].format(email)

        code = redis_utils.get_value(user_key)
        if not code or code != user_code:
            raise exceptions.CodeIsWrong()

        redis_utils.remove_key(user_key)

        # TODO: notification

        # create jwt tokens
        tokens = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'user_role': user.role
        }
        return Response(serializers.TokenResponseSerializer(response_data).data)


class Logout(ms.SwaggerViewMixin, APIView):
    """
        need to destroy access token from client side
    """
    swagger_title = 'Logout'
    swagger_tags = ['Account']
    serializer = serializers.RefreshTokenSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request, *args, **kwargs):

        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refresh_token = ser.validated_data['refresh']
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass
        return Response(serializers.MessageSerializer({'message': 'bye...'}).data)


class Register(ms.SwaggerViewMixin, APIView):
    """
        Register user and return user tokens
    """
    swagger_title = 'Register user'
    swagger_tags = ['Account']
    swagger_response_code = 201
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.RegisterSerializer
    serializer_response = serializers.TokenResponseSerializer

    @transaction.atomic
    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # check OTP
        email = ser.validated_data['email']
        otp_code = ser.validated_data['otp_code']
        conf = settings.USER_OTP_CONFIG
        user_key = conf['STORE_BY'].format(email)

        #check key
        redis_otp = redis_utils.get_value(user_key)
        if not redis_otp or redis_otp != otp_code:
            raise exceptions.CodeIsWrong()

        # create user
        user = ser.save()

        # create jwt tokens
        tokens = RefreshToken.for_user(user)
        tokens_dict = {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'user_role': user.role
        }

        # TODO: notification

        return Response(self.serializer_response(tokens_dict).data, status=status.HTTP_201_CREATED)


class ResetPassword(ms.SwaggerViewMixin, APIView):
    """
        reset password
        create and send reset code
    """
    swagger_title = 'Reset password send code'
    swagger_tags = ['Account']
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.EmailSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        # get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.UserNotFound()

        conf = settings.RESET_PASSWORD_CONFIG
        user_key = conf['STORE_BY'].format(email)

        # check user request(if have previous request)
        if redis_utils.get_value(user_key):
            # reset code has already been sent
            raise exceptions.CodeHasAlreadyBeenSent()

        # generate and set code on redis
        reset_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, reset_code, conf['TIMEOUT'])

        # TODO: notification

        res = {'message': _('Password recovery code sent.')}
        return Response(self.serializer_response(res).data)


class ResetPasswordCheckAndSet(ms.SwaggerViewMixin, APIView):
    """
        reset password
        check code and set new password
    """
    swagger_title = 'Reset password check and set'
    swagger_tags = ['Account']
    permission_classes = (base_permissions.AllowAny,)
    serializer = serializers.ResetPasswordCheckSetPasswordSerializer
    serializer_response = serializers.MessageSerializer

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        user_code = ser.validated_data['code']

        # get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.UserNotFound()

        conf = settings.RESET_PASSWORD_CONFIG
        user_key = conf['STORE_BY'].format(email)

        # check reset code
        code = redis_utils.get_value(user_key)
        if not code:
            # reset code not match(is wrong)
            raise exceptions.CodeIsWrong()

        if not code == user_code:
            # reset code not match(is wrong)
            raise exceptions.CodeIsWrong()

        # clear key
        redis_utils.remove_key(user_key)
        # set password user
        password = ser.validated_data['password']
        user.set_password(password)

        # TODO: notification

        res = {'message': _('Your password has been successfully changed')}
        return Response(self.serializer_response(res).data)


class ConfirmEmail(APIView):
    """
        confirm email
        send code
    """
    serializer_response = serializers.MessageSerializer

    @swagger_auto_schema(
        tags=['Account'],
        operation_id='Confirm email. send code',
        responses={200: serializers.MessageSerializer}
    )
    def get(self, request):
        user = request.user
        email = user.email

        conf = settings.CONFIRM_PHONENUMBER_CONFIG
        user_key = conf['STORE_BY'].format(email)

        # check code request(if have previous request)
        if redis_utils.get_value(user_key):
            # confirm code has already been sent
            raise exceptions.CodeHasAlreadyBeenSent()

        code = utils.random_num(conf['CODE_LENGTH'])

        redis_utils.set_value_expire(user_key, code, conf['TIMEOUT'])

        # TODO: notification

        res = {'message': _('Confirm code sent')}
        return Response(self.serializer_response(res).data)

    @swagger_auto_schema(tags=['Account'],
                         operation_id='Confirm email. check code and confirm',
                         request_body=serializers.ConfirmEmailSerializer,
                         responses={200: serializers.MessageSerializer})
    def post(self, request):

        ser = serializers.ConfirmEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        user = request.user
        email = user.email
        user_code = ser.validated_data['code']

        conf = settings.CONFIRM_PHONENUMBER_CONFIG
        user_key = conf['STORE_BY'].format(email)

        # check code
        code = redis_utils.get_value(user_key)

        if not code:
            # confirm code is not exists
            raise exceptions.CodeIsWrong()

        if not code == user_code:
            # confirm code is not match(is wrong)
            raise exceptions.CodeIsWrong()

        # clear key
        redis_utils.remove_key(user_key)

        # TODO: notification

        res = {'message': _('Your email confirmed successfully')}
        return Response(self.serializer_response(res).data)


class UserSendOTP(ms.SwaggerViewMixin, APIView):
    """
        send otp code user
    """
    swagger_title = 'Send otp code for user'
    swagger_tags = ['Account']
    serializer = serializers.EmailSerializer
    serializer_response = serializers.MessageSerializer
    permission_classes = (base_permissions.AllowAny,)

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser['email'].value
        user = models.User.objects.available_users.get(email=email)

        try:
            user = models.User.objects.available_users.get(email=email)
            if request.data.get('request_type') == 'register':
                raise exceptions.UserIsExists()
        except models.User.DoesNotExist:
            pass

        conf = settings.USER_OTP_CONFIG
        user_key = conf['STORE_BY'].format(email)

        # check key(code)
        if redis_utils.get_value(user_key):
            raise exceptions.CodeHasAlreadyBeenSent()

        # generate and set code on redis
        otp_code = utils.random_num(conf['CODE_LENGTH'])
        redis_utils.set_value_expire(user_key, otp_code, conf['TIMEOUT'])

        # TODO: notification

        res = {'message': _('Register otp code sent')}
        return Response(self.serializer_response(res).data)
# ---------------------------------------------------------------


