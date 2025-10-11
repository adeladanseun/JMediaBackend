from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'get_full_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined', )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'phone_number', 'location')}),
        ('Professional Info', {'fields': ('role', 'skills', 'website', 'github', 'linkedin', 'twitter')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_verified', 'is_active')
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)