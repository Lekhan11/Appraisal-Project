from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CreateUser, UserProfile

@admin.register(CreateUser)
class CustomUserAdmin(UserAdmin):
    model = CreateUser
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'department', 'designation', 'phone_number')

admin.site.register(UserProfile)