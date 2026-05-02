from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.retrospectives.urls")),
]
