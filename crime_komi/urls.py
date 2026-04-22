from django.contrib import admin
from django.urls import path, include, include, include

urlpatterns = [
    path('password-reset/', include('django.contrib.auth.urls')),
    path('password-reset/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('incidents.urls')),
]
