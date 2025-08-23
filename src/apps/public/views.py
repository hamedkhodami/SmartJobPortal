from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView, ListView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import get_messages


from apps.account.mixins import AccessRequiredMixin
from .forms import ContactUsForm, ContactUsReplyForm
from .models import ContactUs


class ContactUsView(LoginRequiredMixin, FormView):
    form_class = ContactUsForm
    template_name = 'public/contactus.html'
    success_url = reverse_lazy('dashboard:dashboard')

    error_redirect_url = reverse_lazy('dashboard:dashboard')

    success_message = _('Your message has been sent successfully.')
    error_message = _('Please check the form for errors.')

    def dispatch(self, request, *args, **kwargs):
        storage = get_messages(request)
        list(storage)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return HttpResponseRedirect(self.error_redirect_url)


class ContactUsListView(LoginRequiredMixin, AccessRequiredMixin, ListView):
    model = ContactUs
    template_name = 'public/contact_list.html'
    context_object_name = 'contacts'
    roles = ['admin']
    paginate_by = 5

    def get_queryset(self):
        return ContactUs.objects.filter(is_read=False).order_by('-created_at')


class ContactUsReplyView(LoginRequiredMixin, AccessRequiredMixin, FormView):
    form_class = ContactUsReplyForm
    template_name = 'public/contact_reply.html'
    roles = ['admin']

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(ContactUs, pk=kwargs.get('pk'))
        if self.contact.is_replied:
            messages.error(request, _('This contact has already been replied to.'))
            return redirect('public:contact_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.contact = self.contact
        reply.responder = self.request.user
        reply.save()
        self.contact.is_replied = True
        self.contact.save()
        messages.success(self.request, _('Reply sent successfully.'))
        return redirect('public:contact_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact'] = self.contact
        return context


class AboutUsView(LoginRequiredMixin, TemplateView):
    template_name = 'public/about.html'


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'public/help.html'
