from django.utils.translation import gettext as _
from django.shortcuts import redirect
from .enums import UserRoleEnum
from django.core.exceptions import PermissionDenied


class LogoutRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)


class AccessRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        allowed_roles = [UserRoleEnum.ADMIN]
        if not request.user.is_superuser and request.user.role not in allowed_roles:
            raise PermissionDenied(_("You do not have permission to this work."))
        return super().dispatch(request, *args, **kwargs)
