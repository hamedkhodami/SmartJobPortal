from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactUs, ContactUsReply


class ContactUsForm(forms.ModelForm):

    class Meta:
        model = ContactUs
        fields = ['title', 'email']

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise forms.ValidationError(_('Title must be at least 3 characters long.'))
        return title

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email or '@' not in email:
            raise forms.ValidationError(_('Enter a valid email address.'))
        return email.lower()


class ContactUsReplyForm(forms.ModelForm):
    class Meta:
        model = ContactUsReply
        fields = ['reply_text']
        labels = {
            'reply_text': _('Reply'),
        }
