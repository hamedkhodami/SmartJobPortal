from django.contrib import admin
from .models import JobModel, ApplicationModel
from django.utils.translation import gettext_lazy as _


@admin.register(JobModel)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'employer_email',
        'employment_type',
        'salary_range_display',
        'is_approved',
        'is_closed',
        'is_active_display',
        'created_at',
    )
    list_filter = (
        'is_approved',
        'is_closed',
        'employment_type',
    )
    search_fields = (
        'title',
        'description',
        'location',
        'employer__email',
    )
    autocomplete_fields = ('employer',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    @admin.display(description=_('Employer'))
    def employer_email(self, obj):
        return obj.employer.email

    @admin.display(description=_('Salary range'))
    def salary_range_display(self, obj):
        return obj.salary_range()

    @admin.display(boolean=True, description=_('Is active'))
    def is_active_display(self, obj):
        return obj.is_active()


@admin.register(ApplicationModel)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'seeker_email',
        'job_title',
        'status',
        'has_resume_display',
        'is_pending_display',
        'created_at',
    )
    list_filter = (
        'status',
        'job__employment_type',
        'job__is_closed',
    )
    search_fields = (
        'seeker__email',
        'job__title',
        'cover_letter',
    )
    autocomplete_fields = ('seeker', 'job')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    @admin.display(description=_('Seeker'))
    def seeker_email(self, obj):
        return obj.seeker.email

    @admin.display(description=_('Job'))
    def job_title(self, obj):
        return obj.job.title

    @admin.display(boolean=True, description=_('Has resume'))
    def has_resume_display(self, obj):
        return obj.has_resume()

    @admin.display(boolean=True, description=_('Is pending'))
    def is_pending_display(self, obj):
        return obj.is_pending()
