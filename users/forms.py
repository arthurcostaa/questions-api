from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from users.models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'name', 'is_active', 'is_admin']
