import os
from pathlib import Path
from dotenv import load_dotenv
from corsheaders.defaults import default_headers


load_dotenv()


def _csv_env(name, default=""):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]


# APPLICATIONS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "drf_spectacular",

    "apps.core",
    "apps.users",
]


# REST FRAMEWORK

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler",
}


# MIDDLEWARE

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # CORS MUST BE HIGH IN MIDDLEWARE
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# TEMPLATES

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


# DATABASE

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.getenv("MONGO_DB_URI"),
        "NAME": os.getenv("MONGO_DB_NAME"),
    }
}


AUTH_USER_MODEL = "users.User"


# PASSWORD VALIDATION

AUTH_PASSWORD_VALIDATORS = []


# INTERNATIONALIZATION

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# STATIC FILES

STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"


SILENCED_SYSTEM_CHECKS = [
    "mongodb.E001",
]


# CUSTOM SECRET KEYS

SECRET_KEY_FOR_STAFF_USER = os.getenv("SECRET_KEY_FOR_STAFF_USER")
SECRET_KEY_FOR_ADMIN_USER = os.getenv("SECRET_KEY_FOR_ADMIN_USER")


# -----------------------------
# CORS SETTINGS
# -----------------------------

CORS_ALLOWED_ORIGINS = _csv_env(
    "CORS_ALLOWED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500",
)

CORS_ALLOW_CREDENTIALS = True


# Allow common headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]


# Allow common HTTP methods

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]


# -----------------------------
# CSRF SETTINGS
# -----------------------------

CSRF_TRUSTED_ORIGINS = _csv_env(
    "CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500",
)


# -----------------------------
# DIGITAL OCEAN SPACES
# -----------------------------

DO_SPACES_KEY = os.getenv("DO_SPACES_KEY")
DO_SPACES_SECRET = os.getenv("DO_SPACES_SECRET")
DO_SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET")
DO_SPACES_REGION = os.getenv("DO_SPACES_REGION")
DO_SPACES_ENDPOINT = os.getenv("DO_SPACES_ENDPOINT")
DO_SPACES_BASE_URL = os.getenv("DO_SPACES_BASE_URL")