from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, password=None, email=None):

        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):

        if not email:
            raise ValueError(_('Users must have a email!'))

        user = self.create_user(password, email)

        user.is_admin = True
        user.is_superuser = True
        user.is_verified = True

        user.save(using=self._db)

        return user
