from apps.core.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class UserNotFound(APIException):
    status_code = 404
    default_code = 'user_not_found'
    message = _('User not found')


class CodeHasAlreadyBeenSent(APIException):
    status_code = 409
    default_code = 'code_already_has_been_send'
    message = _('Code already has been send')


class CodeIsWrong(APIException):
    status_code = 409
    default_code = 'code_is_wrong'
    message = _('The code is wrong or timeout')


class UserIsExists(APIException):
    status_code = 409
    default_code = 'user_is_exist'
    message = _('User already has exited')




