from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("tracker.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
