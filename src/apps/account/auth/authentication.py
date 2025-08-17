from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication


class BaseJWTAuthentication(JWTAuthentication):

    def authenticate(self, request, *args, **kwargs):
        auth = super().authenticate(request)
        if not auth:
            return None
        user, token = auth
        if getattr(user, "is_blocked", False):
            raise exceptions.AuthenticationFailed(_('User in block list'), code='user_blocked')
        return user, token
