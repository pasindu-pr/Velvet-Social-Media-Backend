from django.contrib import admin
from django.urls import path
from django.urls.conf import include 
 
admin.site.site_header = 'Velvet Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('socialmedia/', include('socialmedia.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('__debug__/', include('debug_toolbar.urls')),
]
