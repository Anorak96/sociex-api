from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_admin', 'is_active')
    list_filter = ('is_admin',)
    fieldsets = (
        ('Info', {'fields': ('email', 'username', 'bio', 'password', 'date_joined')}),
        ('Pictures', {'fields': ('profile_pic', 'cover_pic')}),
        ('Relationship', {'fields': ('follower', 'following')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'is_superuser', 'is_staff')}),
        (None, {'fields': ('hide_email', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('date_joined', 'last_login')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.site_header = "Sociama Admin"
admin.site.site_title = "Sociama Admin Portal"
admin.site.index_title = "Welcome to Sociama Network Portal"