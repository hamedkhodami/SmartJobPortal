from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JobConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.job'
    verbose_name = _('Job')
