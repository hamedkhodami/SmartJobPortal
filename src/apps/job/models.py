from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from . import enums


class JobModel(BaseModel):
    TYPE = enums.EmploymentType

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
                                 , verbose_name=_('Employer'))
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    location = models.CharField(_('Location'), max_length=150, null=True, blank=True)
    employment_type = models.CharField(_('Employment type'), max_length=20, choices=TYPE)
    salary_min = models.IntegerField(_('Salary min'), null=True, blank=True)
    salary_max = models.IntegerField(_('Salary max'), null=True, blank=True)
    is_approved = models.BooleanField(_('Is approved'), default=False)
    is_closed = models.BooleanField(_('Is closed'), default=False)

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

    def __str__(self):
        return f"{self.title} - {self.employer.email}"

    def is_active(self):
        return self.is_approved and not self.is_closed

    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"From {self.salary_min:,}"
        elif self.salary_max:
            return f"Up to {self.salary_max:,}"
        return _("Not specified")


class ApplicationModel(BaseModel):
    STATUS_CHOICES = enums.STATUS

    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="applications"
                            , verbose_name=_('Job'))
    seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="applications", verbose_name=_('Seeker'))
    cover_letter = models.TextField(_('Cover letter'), null=True, blank=True)
    resume = models.FileField(_('Resume'), upload_to="resumes/", null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES.SUBMITTED)

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')

    def __str__(self):
        return f"{self.seeker.email} → {self.job.title}"

    def has_resume(self):
        return bool(self.resume)

    def is_pending(self):
        return self.status == enums.STATUS.SUBMITTED