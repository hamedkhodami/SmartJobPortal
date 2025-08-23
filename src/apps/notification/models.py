from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings

from apps.core.models import BaseModel


class EmailNotificationModel(BaseModel):

    title = models.CharField(_('email title'), max_length=130)
    description = models.TextField(_('description'), max_length=500, null=True, blank=True)
    send_email = models.BooleanField(_('send email'), default=True)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('to user'), on_delete=models.CASCADE, related_name='email_notifications')

    class Meta:
        verbose_name = _('Email Notification')
        verbose_name_plural = _('Email Notifications')
        ordering = ('-id',)

    def __str__(self):
        return f'Notification for {self.to_user}'

    def get_title(self):
        return self.title or 'email notification'

    def get_content(self):
        return f"""
            {self.get_title()}
            {self.description}
        """
