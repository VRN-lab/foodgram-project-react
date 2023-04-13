from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as ContribUserAdmin

from .models import User


class UserAdmin(ContribUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')


admin.site.register(User, UserAdmin)
