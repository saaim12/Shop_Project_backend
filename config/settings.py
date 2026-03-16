from pathlib import Path

from corsheaders.defaults import default_headers
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="unsafe-secret-key")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "apps.core",
    "apps.users",
    "apps.cars",
    "apps.spare_parts",
    "apps.tyres",
    "apps.rims",
    "apps.orders",
    "apps.inventory",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.APIErrorLoggingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "config.jwt_auth.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    # "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
}


# Mongo
MONGO_DB_URI = config("MONGO_DB_URI", default="")
MONGO_DB_NAME = config("MONGO_DB_NAME", default="shop_db")


# JWT
JWT_SECRET = config("JWT_SECRET", default=SECRET_KEY)
JWT_ALGORITHM = config("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_MINUTES = config("JWT_ACCESS_TOKEN_MINUTES", default=60, cast=int)
JWT_REFRESH_TOKEN_DAYS = config("JWT_REFRESH_TOKEN_DAYS", default=7, cast=int)


# Role Keys
SECRET_KEY_FOR_STAFF_USER = config("SECRET_KEY_FOR_STAFF_USER", default="")
SECRET_KEY_FOR_ADMIN_USER = config("SECRET_KEY_FOR_ADMIN_USER", default="")


# DigitalOcean Spaces configuration
DO_SPACES_KEY = config("DO_SPACES_KEY", default="")
DO_SPACES_SECRET = config("DO_SPACES_SECRET", default="")
DO_SPACES_BUCKET = config("DO_SPACES_BUCKET", default="")
DO_SPACES_REGION = config("DO_SPACES_REGION", default="")
DO_SPACES_ENDPOINT = config("DO_SPACES_ENDPOINT", default="")
DO_SPACES_BASE_URL = config("DO_SPACES_BASE_URL", default="")

# Upload folders
S3_USERS_FOLDER = config("S3_USERS_FOLDER", default="users")
S3_CARS_FOLDER = config("S3_CARS_FOLDER", default="cars")
S3_SPARE_PARTS_FOLDER = config("S3_SPARE_PARTS_FOLDER", default="spare_parts")
S3_TYRES_FOLDER = config("S3_TYRES_FOLDER", default="tyres")
S3_RIMS_FOLDER = config("S3_RIMS_FOLDER", default="rims")


# S3 enabled flag
USE_S3_STORAGE = all(
    [
        DO_SPACES_KEY,
        DO_SPACES_SECRET,
        DO_SPACES_BUCKET,
        DO_SPACES_REGION,
        DO_SPACES_ENDPOINT,
        DO_SPACES_BASE_URL,
    ]
)


CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=True, cast=bool)
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CORS_ALLOW_HEADERS = list(default_headers) + ["authorization", "content-type"]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


MIGRATION_MODULES = {
    "users": None,
    "cars": None,
    "spare_parts": None,
    "tyres": None,
    "rims": None,
    "orders": None,
    "inventory": None,
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        }
    },
    "handlers": {
        "app_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "app": {
            "handlers": ["app_file"],
            "level": "ERROR",
            "propagate": False,
        }
    },
}