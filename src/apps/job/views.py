from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, DetailView, FormView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

from apps.core.utils import validate_form, toast_form_errors

from .models import JobModel, ApplicationModel
from .forms import JobForm, ApplicationForm
from .mixins import JobEmployerRequiredMixin, JobSeekerRequiredMixin
from .enums import STATUS


class JobListView(LoginRequiredMixin, ListView):
    model = JobModel
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        qs = JobModel.objects.filter(is_approved=True, is_closed=False).order_by('-created_at')
        employment_type = self.request.GET.get('employment_type')
        if employment_type and employment_type != 'all':
            qs = qs.filter(employment_type=employment_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employment_type_selected'] = self.request.GET.get('employment_type', 'all')
        context['employment_type_choices'] = [('all', _('All'))] + list(JobModel.TYPE.choices)
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    model = JobModel
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return JobModel.objects.filter(is_approved=True, is_closed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        job = self.get_object()

        context['can_apply'] = getattr(user, 'role', None) != 'employer'
        context['has_applied'] = False

        if user.is_authenticated and context['can_apply']:
            context['has_applied'] = job.applications.filter(seeker=user).exists()

        return context


class JobCreateView(LoginRequiredMixin, JobEmployerRequiredMixin, CreateView):
    model = JobModel
    form_class = JobForm
    template_name = 'jobs/employer/job_create.html'
    success_url = reverse_lazy('public:index')

    def form_valid(self, form):
        form.instance.employer = self.request.user
        messages.success(self.request, _('Job posting created successfully.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        validate_form(self.request, form)
        toast_form_errors(self.request, form)
        return super().form_invalid(form)


class EmployerJobListView(LoginRequiredMixin, JobEmployerRequiredMixin, ListView):
    model = JobModel
    template_name = 'jobs/employer/employer_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        return JobModel.objects.filter(employer=self.request.user).order_by('-created_at')


class EmployerApplicationListView(LoginRequiredMixin, JobEmployerRequiredMixin, ListView):
    model = ApplicationModel
    template_name = 'jobs/employer/employer_application_list.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return (ApplicationModel.objects
                .filter(job__employer=self.request.user, status='submitted')
                .select_related('job', 'seeker')
                .order_by('-created_at'))


class ApplicationApproveView(LoginRequiredMixin, JobEmployerRequiredMixin, View):
    def post(self, request, pk):
        app = get_object_or_404(ApplicationModel, pk=pk, job__employer=request.user)
        app.status = 'accepted'
        app.save()

        app.job.is_closed = True
        app.job.save()

        messages.success(request, _('Application accepted and job closed.'))
        return redirect('job:employer_applications')


class ApplicationRejectView(LoginRequiredMixin, JobEmployerRequiredMixin, View):
    def post(self, request, pk):
        app = get_object_or_404(ApplicationModel, pk=pk, job__employer=request.user)
        app.status = 'rejected'
        app.save()

        messages.info(request, _('Application rejected.'))
        return redirect('job:employer_applications')


class EmployerJobDeleteView(LoginRequiredMixin, JobEmployerRequiredMixin, DeleteView):
    model = JobModel
    template_name = 'jobs/employer/employer_job_confirm_delete.html'
    success_url = reverse_lazy('job:employer-job-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj


class EmployerAcceptedJobsView(LoginRequiredMixin, JobEmployerRequiredMixin, ListView):
    model = ApplicationModel
    template_name = 'jobs/employer/employer_accepted_jobs.html'
    context_object_name = 'accepted_jobs'
    paginate_by = 10

    def get_queryset(self):
        return (ApplicationModel.objects
                .filter(job__employer=self.request.user, status='accepted')
                .select_related('job', 'seeker')
                .order_by('-created_at'))


class EmployerJobUpdateView(LoginRequiredMixin, JobEmployerRequiredMixin, UpdateView):
    model = JobModel
    form_class = JobForm
    template_name = 'jobs/employer/employer_job_form.html'
    context_object_name = 'job'
    success_url = reverse_lazy('job:employer-job-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.employer != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied(_("You do not have permission to edit this job posting."))
        return obj


class JobApplyView(LoginRequiredMixin, JobSeekerRequiredMixin, FormView):
    form_class = ApplicationForm
    template_name = 'jobs/seeker/job_apply.html'

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(JobModel, pk=self.kwargs['pk'], is_approved=True, is_closed=False)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        if ApplicationModel.objects.filter(job=self.job, seeker=user).exists():
            messages.warning(self.request, _("You have already applied for this job."))
            return redirect('job:job_detail', pk=self.job.pk)

        application = form.save(commit=False)
        application.job = self.job
        application.seeker = user
        application.status = STATUS.SUBMITTED

        application.save()

        messages.success(self.request, _("Your application has been submitted."))
        return redirect('job:job_detail', pk=self.job.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job
        return context


class MyApplicationsView(LoginRequiredMixin, JobSeekerRequiredMixin, ListView):
    model = ApplicationModel
    template_name = 'jobs/seeker/my_applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return ApplicationModel.objects.select_related('job').filter(seeker=self.request.user).order_by('-created_at')


class CancelApplicationView(LoginRequiredMixin, JobSeekerRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(ApplicationModel, pk=pk, seeker=request.user)
        application.delete()
        messages.success(request, _("Your application has been cancelled."))
        return redirect('job:my_applications')
