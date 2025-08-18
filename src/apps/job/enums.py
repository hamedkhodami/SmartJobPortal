from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class EmploymentType(TextChoices):

    FULL_TIME = 'full_time', _('Full time')
    PART_TIME = 'part_time', _('Part time')
    REMOTE = 'remote', _('Remote')
    INTERNSHIP = 'internship', _('Internship')


class STATUS(TextChoices):

    SUBMITTED = 'submitted', _('Submitted')
    REJECTED = 'rejected', _('Rejected')
    ACCEPTED = 'accepted', _('Accepted')

