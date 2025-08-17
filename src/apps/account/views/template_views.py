from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.views.generic import FormView, RedirectView, DetailView, UpdateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.contrib import messages


from random import randint

from ..models import UserProfileModel, User
from ..mixins import LogoutRequiredMixin, AccessRequiredMixin
from ..forms import LoginForm, GetEmailForm, ResetPassForm, VerifyEmailForm, RegisterForm, EditProfileForm
from apps.core.utils import validate_form, toast_form_errors


class LoginView(LogoutRequiredMixin, FormView):

    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('public:index')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, _('You are successfully logged in.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        validate_form(self.request, form)
        return super().form_invalid(form)


class RegisterView(LogoutRequiredMixin, FormView):
    template_name = 'account/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('account:login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, _('Registration successful. You can now log in.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct the errors below.'))
        return super().form_invalid(form)


class GetPhoneNumberView(LogoutRequiredMixin, FormView):
    template_name = 'account/password/forget_code.html'
    form_class = GetEmailForm

    def get_success_url(self):
        return reverse('account:send_code') + f'?next={reverse("account:reset_pass_confirm")}'

    def form_valid(self, form):
        user = form.cleaned_data.get('user')

        # Create register token and save it in sessions
        token = user.generate_token()
        self.request.session['secret_token'] = token

        return super().form_valid(form)

    def form_invalid(self, form):
        toast_form_errors(self.request, form)
        return super().form_invalid(form)


class SendCodeView(LogoutRequiredMixin, View):
    def get_redirect_url(self):
        next_url = self.request.GET.get('next', reverse('account:verify_phone'))
        return next_url

    def get(self, request):
        code = randint(10000, 99999)
        request.session['verify_code'] = code

        token = request.session.get('secret_token')
        try:
            user = User.objects.get(token=token)
        except User.DoesNotExist:
            messages.error(request, _('There is an issue! please try again'))
            return redirect('account:register')

        # TODO:notification

        messages.info(request, _('Code sent to you'))
        return redirect(self.get_redirect_url())


class VerifyEmailView(LogoutRequiredMixin, FormView):
    template_name = 'account/verify_email.html'
    form_class = VerifyEmailForm
    success_url = reverse_lazy('')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method == 'POST':
            kwargs['data'] = {
                'code': self.request.POST.get('code'),
                'verify_code': self.request.session.get('verify_code'),
                'token': self.request.session.get('secret_token')
            }

        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data.get('user')

        # Verify user and clear token
        user.is_verified = True
        user.clear_token(self.request)
        login(self.request, user)

        # Delete code from session
        if 'verify_code' in self.request.session:
            del self.request.session['verify_code']

        messages.success(self.request, _('Register done successful'))
        return redirect('public:index')

    def form_invalid(self, form):
        toast_form_errors(self.request, form)
        return super().form_invalid(form)


class ResetPassConfirmView(LogoutRequiredMixin, FormView):
    template_name = 'account/password/reset_pass_confirm.html'
    form_class = VerifyEmailForm
    success_url = reverse_lazy('account:reset_pass_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method == 'POST':
            kwargs['data'] = {
                'code': self.request.POST.get('code'),
                'verify_code': self.request.session.get('verify_code'),
                'token': self.request.session.get('secret_token')
            }

        return kwargs

    def form_valid(self, form):
        # Delete code from session
        if 'verify_code' in self.request.session:
            del self.request.session['verify_code']

        return super().form_valid(form)

    def form_invalid(self, form):
        toast_form_errors(self.request, form)
        return super().form_invalid(form)


class ResetPassCompleteView(LogoutRequiredMixin, FormView):
    template_name = 'account/password/reset_pass_complete.html'
    form_class = ResetPassForm
    success_url = reverse_lazy('account:login')

    def form_valid(self, form):
        password = form.cleaned_data.get('password2')
        token = self.request.session.get('secret_token')

        try:
            user = User.objects.get(token=token)
        except User.DoesNotExist:
            messages.error(self.request, _('There is an issue! please try again'))
            return self.form_invalid(form)

        # Set new password and clear tokens
        user.set_password(password)
        user.is_verified = True
        user.clear_token(self.request)

        messages.success(self.request, _('Password successfully reset'))
        return super().form_valid(form)

    def form_invalid(self, form):
        toast_form_errors(self.request, form)
        return super().form_invalid(form)


class logoutView(LoginRequiredMixin, RedirectView):

    url = reverse_lazy('account:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, _('You have been logged out'))
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'account/profile.html'
    model = UserProfileModel
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfileModel
    form_class = EditProfileForm
    template_name = 'account/edit_profile.html'
    success_url = reverse_lazy('account:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        # Save profile form
        response = super().form_valid(form)

        user = self.request.user
        user.first_name = self.request.POST.get('first_name', user.first_name)
        user.last_name = self.request.POST.get('last_name', user.last_name)
        user.save(update_fields=['first_name', 'last_name'])

        messages.success(self.request, _('Your profile has been updated successfully.'))
        return response


class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = 'account/user_detail.html'
    model = User
    context_object_name = 'user'
