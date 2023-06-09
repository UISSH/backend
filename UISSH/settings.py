"""
Django settings for UISSH project.
"""

import logging
import os

from corsheaders.defaults import default_headers

from . import BASE_DIR, config
from .components import geo_ip
from .components.common import *

SECRET_KEY = config("DJANGO_SECRET_KEY")


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = config("DEBUG", default=False, cast=bool)

# 不是开发环境，则把会话信息缓存到进程内存中
if not DEBUG:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "\033[1;32m{levelname:5s}\033[0m  \033[0;32m{asctime}\033[0m {name} {pathname}:{lineno} \n\033[0;32m{message}\033[0m",
            "style": "{",
        },
        "simple": {
            "format": "{levelname:5s} {asctime} -> {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "asyncio": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
        },
        "daphne": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
        },
        "urllib3": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
        },
        "docker": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default=["http://localhost:8080"],
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default=["http://localhost:8080"],
)

CORS_ALLOW_HEADERS = list(default_headers) + [
    "anonymous",
]

if DEBUG:
    CORS_ALLOW_HEADERS.append("range")

WEBSITE_ADDRESS = config("WEBSITE_ADDRESS")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'


EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
FROM_EMAIL_ADDRESS = config("FROM_EMAIL_ADDRESS")
DEFAULT_FROM_EMAIL = FROM_EMAIL_ADDRESS

# Application definition

GEOIP_PATH = geo_ip.GEOIP_PATH
INSTALLED_APPS += [
    "websocket",
    "channels",
    "filebrowser.apps.FilebrowserConfig",
]

MIDDLEWARE += []

DEBUG_TOOL = config("DEBUG_TOOL", default=False, cast=bool)

if DEBUG and DEBUG_TOOL:
    INSTALLED_APPS += ["django_extensions", "debug_toolbar"]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

ASGI_APPLICATION = "UISSH.asgi.application"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_gg_cache",
    },
    "GlobalOperationResCache": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_gg_cache_GlobalOperationResCache",
    },
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
