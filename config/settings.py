"""Django settings for Symmetry Lite backend."""

from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="insecure-dev-key")
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "drf_spectacular",
    "users.apps.UsersConfig",
    "exercise_catalog.apps.ExerciseCatalogConfig",
    "workout_sessions.apps.WorkoutSessionsConfig",
    "social.apps.SocialConfig",
    "workout_plans.apps.WorkoutPlansConfig",
    "demo.apps.DemoConfig",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="symmetry_lite"),
        "USER": config("POSTGRES_USER", default="symmetry_lite"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="symmetry_lite"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://redis:6379/0"),
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    # `X-Test-User-Id` resolves the requesting user. Real authentication is
    # intentionally out of scope (see README); see `users.authentication`.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.XTestUserAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "config.openapi.DomainTaggedAutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Symmetry Lite",
    "DESCRIPTION": "Backend senior technical assessment — interactive API docs.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
