import os
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------
# Load environment variables
# ----------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ----------------------------------------------------
# Core Django Settings
# ----------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# ----------------------------------------------------
# Installed Apps
# ----------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",

    "rest_framework",

    "apps.core",
    "apps.users",
]

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ----------------------------------------------------
# URL Configuration
# ----------------------------------------------------

ROOT_URLCONF = "config.urls"

# ----------------------------------------------------
# Templates
# ----------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ----------------------------------------------------
# WSGI
# ----------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"

# ----------------------------------------------------
# MongoDB Configuration
# ----------------------------------------------------

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": MONGO_DB_URI,
        "NAME": MONGO_DB_NAME,
    }
}

# ----------------------------------------------------
# Custom User Model
# ----------------------------------------------------

AUTH_USER_MODEL = "users.User"

# ----------------------------------------------------
# Password Validators
# ----------------------------------------------------

AUTH_PASSWORD_VALIDATORS = []

# ----------------------------------------------------
# Internationalization
# ----------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True

# ----------------------------------------------------
# Static Files
# ----------------------------------------------------

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

# ----------------------------------------------------
# Silence MongoDB AutoField Warnings for Built-in Apps
# ----------------------------------------------------

SILENCED_SYSTEM_CHECKS = [
    "mongodb.E001",  # Suppress MongoDB AutoField warnings for built-in Django apps
]

# ----------------------------------------------------
# Admin User Key
# ----------------------------------------------------



SECRET_KEY_FOR_STAFF_USER = os.getenv("SECRET_KEY_FOR_STAFF_USER")
SECRET_KEY_FOR_ADMIN_USER = os.getenv("SECRET_KEY_FOR_ADMIN_USER")
# ----------------------------------------------------
# Digital Ocean Spaces (S3 Compatible)
# ----------------------------------------------------

DO_SPACES_KEY = os.getenv("DO_SPACES_KEY")
DO_SPACES_SECRET = os.getenv("DO_SPACES_SECRET")
DO_SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET")
DO_SPACES_REGION = os.getenv("DO_SPACES_REGION")
DO_SPACES_ENDPOINT = os.getenv("DO_SPACES_ENDPOINT")
DO_SPACES_BASE_URL = os.getenv("DO_SPACES_BASE_URL")