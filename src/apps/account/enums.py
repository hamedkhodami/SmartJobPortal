from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class UserRoleEnum(TextChoices):

    ADMIN = 'admin', _('Admin')
    EMPLOYER = 'employer', _('Employer')
    JOB_SEEKER = 'job_seeker', _('Job seeker')


class UserGenderEnum(TextChoices):

    MALE = 'm', _('Male')
    FEMALE = 'f', _('Female')
