from django.contrib import admin 
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.  
@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'email','password','name', 'location','date_joined']

    fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('Permissions', {'fields': ('is_staff', 'is_active')}),
        )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


    ordering = ['email']


    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"