from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import JobModel, ApplicationModel


class JobForm(forms.ModelForm):
    class Meta:
        model = JobModel
        fields = [
            'title',
            'description',
            'location',
            'employment_type',
            'salary_min',
            'salary_max',
            'is_approved',
            'is_closed',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': _('Job Title'),
            'description': _('Job Description'),
            'location': _('Location'),
            'employment_type': _('Employment type'),
            'salary_min': _('Salary min'),
            'salary_max': _('Salary max'),
            'is_approved': _('Is approved'),
            'is_closed': _('Is closed'),
        }
        error_messages = {
            'title': {
                'required': _('Please enter a job title.'),
                'max_length': _('Title is too long.'),
            },
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = ApplicationModel
        fields = ['cover_letter', 'resume']
