# apps/dashboard/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from apps.job.models import JobModel, ApplicationModel
from apps.account.enums import UserRoleEnum
from apps.job.enums import STATUS


User = get_user_model()


class DashboardBaseView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        role_context = {}
        if user.role == UserRoleEnum.EMPLOYER:
            role_context = self.get_employer_context(user)
        elif user.role == UserRoleEnum.JOB_SEEKER:
            role_context = self.get_jobseeker_context(user)
        elif user.role == UserRoleEnum.ADMIN:
            role_context = self.get_admin_context()

        context.update(role_context)
        context["role"] = user.role
        return context

    def get_employer_context(self, user):
        jobs = JobModel.objects.filter(employer=user)
        applications = ApplicationModel.objects.filter(job__employer=user)

        return {
            "jobs_count": jobs.count(),
            "applications_count": applications.count(),
            "accepted_count": applications.filter(status=STATUS.ACCEPTED).count(),
        }

    def get_jobseeker_context(self, user):
        applications = ApplicationModel.objects.filter(seeker=user)

        return {
            "applied_count": applications.count(),
            "accepted_count": applications.filter(status=STATUS.ACCEPTED).count(),
            "rejected_count": applications.filter(status=STATUS.REJECTED).count(),
        }

    def get_admin_context(self):
        return {
            "pending_jobs": JobModel.objects.filter(is_approved=False).count(),
            "active_jobs": JobModel.objects.filter(is_approved=True, is_closed=False).count(),
            "users_count": User.objects.count(),
            "applications_count": ApplicationModel.objects.count(),
        }
