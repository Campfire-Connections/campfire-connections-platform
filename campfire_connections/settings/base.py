"""
Base Django settings for campfire_connections.

Environment-specific overrides live in local.py / prod.py.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured

os.environ.setdefault("SQLITE_TMPDIR", "/tmp")

# project root (one level above the campfire_connections package)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def _env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes"}


# Core config
_using_local_settings = os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith(".local")
DEBUG = _env_flag("DJANGO_DEBUG", default=_using_local_settings)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-wl)9ok1=pgk^yt5(2er0#nf@m40aoa^+fjer#2m)3w!$b194#="
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production.")

ALLOWED_HOSTS = [
    host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host
] or (["localhost", "127.0.0.1"] if DEBUG else [])
if not ALLOWED_HOSTS and not DEBUG:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set in production.")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "django_tables2",
    "taggit",
    "address",
    "core",
    "organization",
    "facility",
    "faction",
    "course",
    "enrollment",
    "reports",
    "pages",
    "user",
    "main",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "campfire_connections.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.dynamic_menu",
                "core.context_processors.top_links_menu",
                "core.context_processors.user_profile",
                "core.context_processors.user_type",
                "core.context_processors.active_enrollment",
                "core.context_processors.color_scheme_processor",
                "core.context_processors.user_info_row",
                "core.context_processors.my_enrollments",
                "core.context_processors.theme_mode",
            ],
        },
    },
]

WSGI_APPLICATION = "campfire_connections.wsgi.application"
ASGI_APPLICATION = "campfire_connections.asgi.application"

DATABASE_ENGINE = os.environ.get("DJANGO_DATABASE_ENGINE", "sqlite").lower()

if DATABASE_ENGINE in {"postgres", "postgresql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "campfireconnections"),
            "USER": os.environ.get("POSTGRES_USER", "campfire"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "campfire"),
            "HOST": os.environ.get("POSTGRES_HOST", "db"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.environ.get("SQLITE_DATABASE_NAME", "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "pages" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_USER_MODEL = "user.User"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

rest_auth_classes = ["rest_framework.authentication.SessionAuthentication"]
if DEBUG:
    rest_auth_classes.append("rest_framework.authentication.BasicAuthentication")

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": rest_auth_classes,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.environ.get("DJANGO_API_PAGE_SIZE", "50")),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": os.environ.get("DJANGO_API_THROTTLE_USER", "1000/day"),
        "anon": os.environ.get("DJANGO_API_THROTTLE_ANON", "100/day"),
    },
}

SESSION_COOKIE_SECURE = _env_flag("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = _env_flag("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = int(
    os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_flag(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG
)
SECURE_HSTS_PRELOAD = _env_flag("DJANGO_SECURE_HSTS_PRELOAD", default=not DEBUG)
SECURE_SSL_REDIRECT = _env_flag("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": (
                '{"level":"%(levelname)s","ts":"%(asctime)s",'
                '"logger":"%(name)s","message":"%(message)s",'
                '"module":"%(module)s","lineno":%(lineno)d}'
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
