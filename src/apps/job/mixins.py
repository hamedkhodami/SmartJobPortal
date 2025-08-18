from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from apps.account.enums import UserRoleEnum


class JobEmployerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        allowed_roles = [UserRoleEnum.ADMIN, UserRoleEnum.EMPLOYER]
        if not request.user.is_superuser and request.user.role not in allowed_roles:
            raise PermissionDenied(_("You do not have permission to this work."))
        return super().dispatch(request, *args, **kwargs)


class JobSeekerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        allowed_roles = [UserRoleEnum.ADMIN, UserRoleEnum.JOB_SEEKER]
        if not request.user.is_superuser and request.user.role not in allowed_roles:
            raise PermissionDenied(_("You do not have permission to this work."))
        return super().dispatch(request, *args, **kwargs)
