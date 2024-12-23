from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/compts/', include('compts.urls')),
    path('api/auth/', include('allauth.urls')),
]