from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import RedirectView


def admin_frontend(request, admin_path=""):
    destination = f"{settings.FRONTEND_URL.rstrip('/')}/admin/"
    if admin_path.startswith("captions/"):
        destination += "?view=captions"
    return redirect(destination)


urlpatterns = [
    path("", RedirectView.as_view(url=settings.FRONTEND_URL, permanent=False), name="site-home"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin_frontend, name="admin-home"),
    path("admin/<path:admin_path>", admin_frontend, name="admin-frontend"),
    path("django-admin/", admin.site.urls),
    path("api/", include("captions.urls")),
]
