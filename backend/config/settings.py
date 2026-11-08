from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
for env_line in (BASE_DIR / ".env").read_text().splitlines() if (BASE_DIR / ".env").exists() else ():
    env_line = env_line.strip()
    if env_line and not env_line.startswith("#") and "=" in env_line:
        env_key, _, env_value = env_line.partition("=")
        os.environ.setdefault(env_key.strip(), env_value.strip().strip("\"'"))
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:4321/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "captions",
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.template.context_processors.i18n",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
if TURSO_DATABASE_URL:
    TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
    if not TURSO_AUTH_TOKEN:
        raise RuntimeError("TURSO_AUTH_TOKEN is required when TURSO_DATABASE_URL is set.")
    DATABASES = {"default": {
        "ENGINE": "django_libsql",
        "NAME": TURSO_DATABASE_URL,
        "AUTH_TOKEN": TURSO_AUTH_TOKEN,
        "OPTIONS": {"timeout": 30},
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "bn"
LANGUAGES = [("bn", "বাংলা"), ("en", "English")]
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:4321,http://127.0.0.1:4321").split(",")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost:4321,http://127.0.0.1:4321").split(",")
