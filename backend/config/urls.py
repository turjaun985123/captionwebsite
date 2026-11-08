from django.contrib import admin
from django.conf import settings
import mimetypes
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.urls import include, path


def frontend_file(relative_path):
    file_path = settings.ASTRO_DIST_DIR / relative_path
    if file_path.is_file():
        return FileResponse(file_path.open("rb"), content_type="text/html; charset=utf-8")
    return redirect(settings.FRONTEND_URL)


def public_frontend(request):
    return frontend_file("index.html")


def frontend_asset(request, asset_path):
    root = settings.ASTRO_DIST_DIR.resolve()
    file_path = (root / asset_path).resolve()
    if not file_path.is_relative_to(root) or not file_path.is_file():
        raise Http404
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    return FileResponse(file_path.open("rb"), content_type=content_type)


def astro_asset(request, asset_path):
    return frontend_asset(request, f"_astro/{asset_path}")


def admin_frontend(request, admin_path=""):
    if admin_path.startswith("captions/"):
        return redirect("/admin/?view=captions")
    return frontend_file("admin/index.html")


urlpatterns = [
    path("", public_frontend, name="site-home"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin_frontend, name="admin-home"),
    path("admin/<path:admin_path>", admin_frontend, name="admin-frontend"),
    path("django-admin/", admin.site.urls),
    path("api/", include("captions.urls")),
    path("_astro/<path:asset_path>", astro_asset, name="astro-asset"),
    path("<path:asset_path>", frontend_asset, name="frontend-asset"),
]
