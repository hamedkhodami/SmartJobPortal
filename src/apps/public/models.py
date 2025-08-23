from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import BaseModel


class ContactUs(BaseModel):

    title = models.CharField(_('Title'), max_length=128)
    email = models.EmailField(_('Email'))

    is_read = models.BooleanField(_('Is read?'), default=False)
    is_replied = models.BooleanField(_('Is replied?'), default=False)

    class Meta:
        verbose_name = _('Contactus')
        verbose_name_plural = _('Contactus')

    def __str__(self):
        return f"{self.title} - {self.email}"


class ContactUsReply(BaseModel):
    contact = models.ForeignKey(ContactUs, on_delete=models.CASCADE, related_name='replies'
                                , verbose_name=_('Contact'))
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
                                  , verbose_name=_('Responder'))
    reply_text = models.TextField(_('Reply text'))

    class Meta:
        verbose_name = _('Contact reply')
        verbose_name_plural = _('Contact replies')

    def __str__(self):
        return f"Reply to {self.contact.email} by {self.responder.email}"