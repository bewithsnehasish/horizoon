from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/admin/')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path("admin/", admin.site.urls),
    path("authentication/", include("authentication.urls")),
    path("business/", include("business.urls")),
    path('cron', include('cron.urls')),
]
