from django.contrib import admin 
from .models import User

# Register your models here.  
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email','name', 'location','date_joined']

    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"