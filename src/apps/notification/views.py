from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import EmailNotificationModel


class NotificationsViews(LoginRequiredMixin, ListView):
    model = EmailNotificationModel
    template_name = 'public/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get_queryset(self):
        return EmailNotificationModel.objects.filter(to_user=self.request.user).order_by('-created_at')
