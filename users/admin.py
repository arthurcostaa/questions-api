from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser

    list_display = ['email', 'name', 'is_active', 'is_admin']
    list_filter = ['is_admin', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('name',)}),
        (
            ('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_admin',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )

    search_fields = ['email', 'name']
    ordering = ['email']
    filter_horizontal = ['groups', 'user_permissions']


admin.site.register(CustomUser, CustomUserAdmin)
