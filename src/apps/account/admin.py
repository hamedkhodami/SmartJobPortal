from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from . import models


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = models.User

    list_display = ('email', 'is_active', 'last_login', 'role')
    list_filter = ('is_active', 'role', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': (
            'email', 'password', 'role', 'first_name', 'last_name',)}),
        ('Permissions',
         {'fields': ('is_active', 'is_admin', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active',
                       'is_admin', 'is_verified', 'first_name', 'last_name',
                       'role')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.UserBlock)
admin.site.register(models.UserProfileModel)
