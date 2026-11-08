import json
from functools import wraps
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Caption


def serialize(caption):
    return {
        "id": caption.pk,
        "text": caption.text,
        "category": caption.category,
        "author": caption.author,
        "likes": caption.likes,
        "featured": caption.is_featured,
        "created_at": caption.created_at.isoformat(),
    }


@require_GET
def caption_list(request):
    captions = Caption.objects.filter(is_published=True)
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if query:
        captions = captions.filter(Q(text__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query))
    if category and category.lower() != "all":
        captions = captions.filter(category__iexact=category)
    items = list(captions[:100])
    categories = list(Caption.objects.filter(is_published=True).values_list("category", flat=True).distinct().order_by("category"))
    return JsonResponse({"results": [serialize(item) for item in items], "categories": categories, "count": len(items)})


@require_POST
def caption_like(request, caption_id):
    updated = Caption.objects.filter(pk=caption_id, is_published=True).update(likes=F("likes") + 1)
    if not updated:
        return JsonResponse({"error": "Caption not found."}, status=404)
    return JsonResponse({"id": caption_id, "likes": Caption.objects.values_list("likes", flat=True).get(pk=caption_id)})


def _admin_payload(caption):
    return {
        "id": caption.pk,
        "text": caption.text,
        "category": caption.category,
        "author": caption.author,
        "likes": caption.likes,
        "is_featured": caption.is_featured,
        "is_published": caption.is_published,
        "created_at": caption.created_at.isoformat(),
        "updated_at": caption.updated_at.isoformat(),
    }


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _staff_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "Sign in with an admin account."}, status=401)
        return view(request, *args, **kwargs)
    return wrapped


@require_GET
@ensure_csrf_cookie
def admin_session(request):
    user = request.user
    return JsonResponse({
        "authenticated": bool(user.is_authenticated and user.is_staff and user.has_perm("captions.view_caption")),
        "username": user.get_username() if user.is_authenticated else "",
        "permissions": {
            "view": bool(user.is_authenticated and user.has_perm("captions.view_caption")),
            "add": bool(user.is_authenticated and user.has_perm("captions.add_caption")),
            "change": bool(user.is_authenticated and user.has_perm("captions.change_caption")),
            "delete": bool(user.is_authenticated and user.has_perm("captions.delete_caption")),
            "view_users": bool(user.is_authenticated and user.has_perm("auth.view_user")),
            "view_groups": bool(user.is_authenticated and user.has_perm("auth.view_group")),
            "add_groups": bool(user.is_authenticated and user.has_perm("auth.add_group")),
            "add_users": bool(user.is_authenticated and user.has_perm("auth.add_user")),
            "change_users": bool(user.is_authenticated and user.has_perm("auth.change_user")),
        },
        "csrfToken": get_token(request),
    })


@require_POST
def admin_login(request):
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Enter a valid username and password."}, status=400)
    user = authenticate(request, username=data.get("username", ""), password=data.get("password", ""))
    if user is None or not user.is_active or not user.is_staff or not user.has_perm("captions.view_caption"):
        return JsonResponse({"error": "The username or password is incorrect."}, status=400)
    login(request, user)
    return JsonResponse({"ok": True, "username": user.get_username(), "csrfToken": get_token(request)})


@require_POST
@_staff_required
def admin_logout(request):
    logout(request)
    return JsonResponse({"ok": True})


@require_GET
@_staff_required
def admin_caption_list(request):
    if not request.user.has_perm("captions.view_caption"):
        return JsonResponse({"error": "You do not have permission to view captions."}, status=403)
    captions = Caption.objects.all()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    featured = request.GET.get("featured", "").strip()
    if query:
        captions = captions.filter(Q(text__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query))
    if category:
        captions = captions.filter(category=category)
    if status in ("published", "draft"):
        captions = captions.filter(is_published=(status == "published"))
    if featured in ("yes", "no"):
        captions = captions.filter(is_featured=(featured == "yes"))
    ordering = request.GET.get("ordering", "-created_at")
    allowed_ordering = {"text", "-text", "category", "-category", "likes", "-likes", "created_at", "-created_at", "updated_at", "-updated_at"}
    if ordering in allowed_ordering:
        captions = captions.order_by(ordering)
    total = captions.count()
    try:
        page = max(1, int(request.GET.get("page", "1")))
        page_size = min(100, max(1, int(request.GET.get("page_size", "20"))))
    except ValueError:
        page, page_size = 1, 20
    start = (page - 1) * page_size
    results = list(captions[start:start + page_size])
    return JsonResponse({
        "results": [_admin_payload(caption) for caption in results],
        "count": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "categories": list(Caption.objects.order_by("category").values_list("category", flat=True).distinct()),
    })


def _validate_caption(data):
    if not isinstance(data, dict):
        return None, {"form": "Enter caption details."}
    text = data.get("text", "")
    category = data.get("category", "অনুভূতি")
    author = data.get("author", "")
    if not isinstance(text, str) or not text.strip():
        return None, {"text": "Caption text is required."}
    if len(text.strip()) > 500:
        return None, {"text": "Caption text must be 500 characters or fewer."}
    if not isinstance(category, str) or not category.strip() or len(category.strip()) > 40:
        return None, {"category": "Enter a category of 40 characters or fewer."}
    if not isinstance(author, str) or len(author.strip()) > 80:
        return None, {"author": "Author name must be 80 characters or fewer."}
    return {
        "text": text.strip(),
        "category": category.strip(),
        "author": author.strip(),
        "is_published": data.get("is_published", True) is True,
        "is_featured": data.get("is_featured", False) is True,
    }, None


@require_http_methods(["GET", "POST"])
@_staff_required
def admin_caption_collection(request):
    if request.method == "GET":
        return admin_caption_list(request)
    if not request.user.has_perm("captions.add_caption"):
        return JsonResponse({"error": "You do not have permission to add captions."}, status=403)
    values, errors = _validate_caption(_json_body(request))
    if errors:
        return JsonResponse({"errors": errors}, status=422)
    caption = Caption.objects.create(**values)
    return JsonResponse({"caption": _admin_payload(caption)}, status=201)


@require_http_methods(["GET", "PATCH", "DELETE"])
@_staff_required
def admin_caption_detail(request, caption_id):
    try:
        caption = Caption.objects.get(pk=caption_id)
    except Caption.DoesNotExist:
        return JsonResponse({"error": "Caption not found."}, status=404)
    if request.method == "GET":
        if not request.user.has_perm("captions.view_caption"):
            return JsonResponse({"error": "You do not have permission to view captions."}, status=403)
        return JsonResponse({"caption": _admin_payload(caption)})
    if request.method == "DELETE":
        if not request.user.has_perm("captions.delete_caption"):
            return JsonResponse({"error": "You do not have permission to delete captions."}, status=403)
        caption.delete()
        return JsonResponse({"ok": True})
    if not request.user.has_perm("captions.change_caption"):
        return JsonResponse({"error": "You do not have permission to edit captions."}, status=403)
    values, errors = _validate_caption(_json_body(request))
    if errors:
        return JsonResponse({"errors": errors}, status=422)
    for field, value in values.items():
        setattr(caption, field, value)
    caption.save()
    return JsonResponse({"caption": _admin_payload(caption)})


@require_POST
@_staff_required
def admin_caption_bulk(request):
    data = _json_body(request)
    if not isinstance(data, dict) or not isinstance(data.get("ids"), list):
        return JsonResponse({"error": "Select at least one caption."}, status=400)
    ids = [pk for pk in data["ids"] if isinstance(pk, int)]
    queryset = Caption.objects.filter(pk__in=ids)
    action = data.get("action")
    if not ids:
        return JsonResponse({"error": "Select at least one caption."}, status=400)
    if action == "delete":
        if not request.user.has_perm("captions.delete_caption"):
            return JsonResponse({"error": "You do not have permission to delete captions."}, status=403)
        count, _ = queryset.delete()
    else:
        if not request.user.has_perm("captions.change_caption"):
            return JsonResponse({"error": "You do not have permission to update captions."}, status=403)
        updates = {"publish": {"is_published": True}, "draft": {"is_published": False}, "feature": {"is_featured": True}, "unfeature": {"is_featured": False}}
        if action not in updates:
            return JsonResponse({"error": "Choose a valid bulk action."}, status=400)
        count = queryset.update(**updates[action])
    return JsonResponse({"ok": True, "count": count})


@require_http_methods(["GET", "POST"])
@_staff_required
def admin_access(request):
    user = request.user
    if request.method == "POST":
        if not user.has_perm("auth.add_group"):
            return JsonResponse({"error": "You do not have permission to create groups."}, status=403)
        data = _json_body(request)
        name = data.get("name", "").strip() if isinstance(data, dict) and isinstance(data.get("name", ""), str) else ""
        if not name:
            return JsonResponse({"errors": {"name": "Enter a group name."}}, status=400)
        if len(name) > 150:
            return JsonResponse({"errors": {"name": "Group name must be 150 characters or fewer."}}, status=400)
        if Group.objects.filter(name__iexact=name).exists():
            return JsonResponse({"errors": {"name": "A group with this name already exists."}}, status=400)
        group = Group.objects.create(name=name)
        return JsonResponse({"id": group.pk, "name": group.name}, status=201)
    can_view_users = user.has_perm("auth.view_user")
    can_view_groups = user.has_perm("auth.view_group")
    if not can_view_users and not can_view_groups:
        return JsonResponse({"error": "You do not have permission to view users or groups."}, status=403)
    query = request.GET.get("q", "").strip()
    users = []
    groups = []
    if can_view_users:
        user_model = get_user_model()
        queryset = user_model.objects.prefetch_related("groups").order_by("username")
        if query:
            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        users = [{
            "id": item.pk,
            "username": item.get_username(),
            "name": item.get_full_name(),
            "email": item.email,
            "is_active": item.is_active,
            "is_staff": item.is_staff,
            "is_superuser": item.is_superuser,
            "groups": list(item.groups.values_list("name", flat=True)),
        } for item in queryset[:250]]
    if can_view_groups:
        queryset = Group.objects.annotate(member_count=Count("user")).prefetch_related("permissions").order_by("name")
        if query:
            queryset = queryset.filter(name__icontains=query)
        groups = [{
            "id": item.pk,
            "name": item.name,
            "member_count": item.member_count,
            "permission_count": len(item.permissions.all()),
        } for item in queryset[:250]]
    return JsonResponse({"can_view_users": can_view_users, "can_view_groups": can_view_groups, "can_add_groups": user.has_perm("auth.add_group"), "can_add_users": user.has_perm("auth.add_user"), "can_change_users": user.has_perm("auth.change_user"), "can_create_admin": user.is_superuser, "users": users, "groups": groups})


@require_POST
@_staff_required
def admin_user_create(request):
    actor = request.user
    if not actor.has_perm("auth.add_user"):
        return JsonResponse({"error": "You do not have permission to create users."}, status=403)
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Enter valid account details."}, status=400)
    username = data.get("username", "").strip() if isinstance(data.get("username", ""), str) else ""
    email = data.get("email", "").strip() if isinstance(data.get("email", ""), str) else ""
    password = data.get("password", "")
    role = data.get("role", "staff")
    User = get_user_model()
    if not username:
        return JsonResponse({"errors": {"username": "Enter a username."}}, status=400)
    if len(username) > 150 or not all(char.isalnum() or char in ".@+-_" for char in username):
        return JsonResponse({"errors": {"username": "Use letters, numbers, and . @ + - or _ in the username."}}, status=400)
    if User._default_manager.filter(username__iexact=username).exists():
        return JsonResponse({"errors": {"username": "This username is already in use."}}, status=400)
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"errors": {"email": "Enter a valid email address."}}, status=400)
    if not isinstance(password, str) or len(password) < 10:
        return JsonResponse({"errors": {"password": "Use a password with at least 10 characters."}}, status=400)
    if role not in ("staff", "admin"):
        return JsonResponse({"errors": {"role": "Choose staff or admin."}}, status=400)
    if role == "admin" and not actor.is_superuser:
        return JsonResponse({"error": "Only a superuser can create an admin account."}, status=403)
    if role == "admin":
        new_user = User._default_manager.create_superuser(username=username, email=email, password=password)
    else:
        new_user = User._default_manager.create_user(username=username, email=email, password=password)
        new_user.is_staff = True
        new_user.save(update_fields=["is_staff"])
        new_user.user_permissions.set(Permission.objects.filter(content_type__app_label="captions", codename__in=["view_caption", "add_caption", "change_caption"]))
    return JsonResponse({"id": new_user.pk, "username": new_user.get_username(), "is_staff": new_user.is_staff, "is_superuser": new_user.is_superuser}, status=201)


@require_POST
@_staff_required
def admin_user_password(request, user_id):
    actor = request.user
    if not actor.has_perm("auth.change_user"):
        return JsonResponse({"error": "You do not have permission to change passwords."}, status=403)
    User = get_user_model()
    target = User._default_manager.filter(pk=user_id).first()
    if target is None:
        return JsonResponse({"error": "User not found."}, status=404)
    if (target.is_superuser or target.is_staff) and not actor.is_superuser:
        return JsonResponse({"error": "Only a superuser can change an admin or staff password."}, status=403)
    data = _json_body(request)
    password = data.get("password", "") if isinstance(data, dict) else ""
    if not isinstance(password, str) or len(password) < 10:
        return JsonResponse({"errors": {"password": "Use a password with at least 10 characters."}}, status=400)
    target.set_password(password)
    target.save(update_fields=["password"])
    return JsonResponse({"ok": True, "id": target.pk})
