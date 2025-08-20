from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.core.validators import OnlyPersianCharsValidator
from .models import User, UserProfileModel
from .enums import UserRoleEnum


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        user = None
        username_is_email = False
        try:
            validate_email(email)
            username_is_email = True
        except ValidationError:
            pass

        if username_is_email:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError(_('Invalid email or password.'))

                if user.is_blocked:
                    raise forms.ValidationError(_('Your account has been blocked. Please contact support.'))

            except User.DoesNotExist:
                raise forms.ValidationError(_('Invalid email or password.'))

        self._user = user
        return {'user': user, 'remember_me': self.cleaned_data.get('remember_me')}

    def get_user(self):
        return self._user


class RegisterForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=225)
    first_name = forms.CharField(
        label=_("First name"),
        max_length=128,
        validators=[OnlyPersianCharsValidator],
        required=False
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=128,
        validators=[OnlyPersianCharsValidator],
        required=False
    )
    role = forms.ChoiceField(
        label=_("Role"),
        choices=[
            (UserRoleEnum.EMPLOYER, UserRoleEnum.EMPLOYER.label),
            (UserRoleEnum.JOB_SEEKER, UserRoleEnum.JOB_SEEKER.label),
        ],
        widget=forms.Select,
        required=True
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=128
    )
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
        max_length=128
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('This email is already registered.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            raise ValidationError(_('Passwords do not match.'))

        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)

        return cleaned_data

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data.get('first_name') or _('No Name'),
            last_name=self.cleaned_data.get('last_name') or _('No Name'),
            role=self.cleaned_data['role'],
            is_active=True,
            is_verified=False
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class VerifyEmailForm(forms.Form):
    code = forms.CharField(max_length=5, required=True, widget=forms.NumberInput)
    verify_code = forms.CharField(max_length=5, required=False, widget=forms.NumberInput)
    token = forms.CharField(max_length=32, required=False, widget=forms.TextInput)

    def clean(self):
        try:
            user = User.objects.get(token=self.cleaned_data['token'])
        except (User.DoesNotExist, TypeError, KeyError):
            raise ValidationError(_('There is an issue! please try again'), code='USER-NOT-FOUND')

        if self.cleaned_data['code'] != self.cleaned_data['verify_code']:
            raise ValidationError(_('Entered code is not correct'), code='WRONG-DATA')

        return {'user': user}


class GetEmailForm(forms.Form):
    email = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'placeholder': '09__'}))

    def clean(self):
        try:
            user = User.objects.get(phone_number=self.cleaned_data['email'])
        except (User.DoesNotExist, TypeError, KeyError):
            raise ValidationError(_('No user found with this email'))
        return {'user': user}


class ResetPassForm(forms.Form):
    password = forms.CharField(max_length=128, min_length=4, required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=128, min_length=4, required=True, widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Passwords are not match.'))

        return password2


class AdminCreationForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    confirm_password = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = UserRoleEnum.ADMIN
        user.is_active = True
        user.is_verified = True
        if commit:
            user.save()
        return user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfileModel
        fields = [
            'phone_number', 'gender', 'bio',
            'image', 'degree', 'city', 'skills'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'phone_number': _('Phone Number'),
            'gender': _('Gender'),
            'bio': _('Biography'),
            'image': _('Profile Image'),
            'degree': _('Degree'),
            'city': _('City'),
            'skills': _('Skills'),
        }
        error_messages = {
            'phone_number': {
                'max_length': _('Phone number must not exceed 11 digits.'),
            },
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)
