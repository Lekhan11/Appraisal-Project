from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CreateUser)
class CustomUserAdmin(UserAdmin):
    model = CreateUser
    list_display = ["username", "email", "department", "designation", "phone_number", "is_staff"]

    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("department", "designation", "phone_number")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("department", "designation", "phone_number")}),
    )

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'department', 'designation', 'phone_number')

admin.site.register(Department)
admin.site.register(Activities)