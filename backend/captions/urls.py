from django.urls import path
from . import views

urlpatterns = [
    path("captions/", views.caption_list, name="caption-list"),
    path("captions/<int:caption_id>/like/", views.caption_like, name="caption-like"),
    path("admin/session/", views.admin_session, name="admin-session"),
    path("admin/login/", views.admin_login, name="admin-login"),
    path("admin/logout/", views.admin_logout, name="admin-logout"),
    path("admin/captions/", views.admin_caption_collection, name="admin-caption-list"),
    path("admin/captions/bulk/", views.admin_caption_bulk, name="admin-caption-bulk"),
    path("admin/captions/<int:caption_id>/", views.admin_caption_detail, name="admin-caption-detail"),
    path("admin/access/", views.admin_access, name="admin-access"),
    path("admin/users/", views.admin_user_create, name="admin-user-create"),
    path("admin/users/<int:user_id>/password/", views.admin_user_password, name="admin-user-password"),
]
