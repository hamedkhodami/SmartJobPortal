from datetime import timedelta
from secrets import token_hex

from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from django.shortcuts import reverse

from apps.core.models import BaseModel
from apps.core.validators import OnlyPersianCharsValidator

from .managers import UserManager
from .enums import UserRoleEnum, UserGenderEnum


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    Role = UserRoleEnum

    email = models.EmailField(_('Email'), max_length=225, null=True, blank=True, unique=True)
    first_name = models.CharField(_('First name'), max_length=128, null=True, blank=True,
                                  default=_('No Name'), validators=[OnlyPersianCharsValidator])
    last_name = models.CharField(_('Last name'), max_length=128, null=True, blank=True,
                                 default=_('No Name'), validators=[OnlyPersianCharsValidator])
    role = models.CharField(_('Role'), max_length=20, choices=Role.choices, default=Role.JOB_SEEKER)
    is_active = models.BooleanField(_('Active'), default=True)
    is_admin = models.BooleanField(_('Admin'), default=False)
    is_verified = models.BooleanField(_('Verify'), default=False)
    token = models.CharField(_("Secret token"), max_length=64, null=True, blank=True, editable=False)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or _('No Name')

    def has_role(self, role_name):
        return self.role == role_name

    def generate_token(self, byte_size=32):
        self.token = token_hex(byte_size)
        self.save(update_fields=['token'])
        return self.token

    def check_token(self, token):
        return self.token == token

    def last_login_within(self, days):
        if self.last_login:
            local_time = timezone.localtime(self.last_login)
            return local_time >= timezone.now() - timedelta(days=days)
        return False

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_blocked(self):
        try:
            self.userblock
            return True
        except ObjectDoesNotExist:
            return False


class UserProfileModel(BaseModel):

    Gender = UserGenderEnum

    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(_('Phone number'), max_length=11)
    gender = models.CharField(_('Gender'), max_length=10, choices=Gender.choices, null=True, blank=True)
    bio = models.TextField(_('Bio'), blank=True, null=True)
    image = models.ImageField(_('Picture'), upload_to='images/profiles/', null=True, blank=True)
    degree = models.CharField(_('Degree'), max_length=128, null=True, blank=True)
    city = models.CharField(_('City'), max_length=64, null=True, blank=True)
    skills = models.TextField(_('Skills'), blank=True, null=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('Users profile')

    def __str__(self):
        return f'{self.user}'

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default/user.jpg')

    def get_absolute_url(self):
        return reverse('account:public_profile', args=[self.pk])


class UserBlock(BaseModel):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='userblock')
    admin = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='user_blocked_by_admin')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Blocked User')
        verbose_name_plural = _('Blocked Users')

    def __str__(self):
        return f'{self.user}'

    def is_blocked_by_admin(self, admin_user):
        return self.admin == admin_user
