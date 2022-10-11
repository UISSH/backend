import os

from . import sentry
from . import spectacular
from .. import BASE_DIR, config

try:
    sentry.__init__()
except:
    pass

AUTH_USER_MODEL = 'common.User'

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'drf_yasg',
    'drf_spectacular',
    'django_filters',
    'corsheaders',
    'django_json_widget',
    'rest_framework',
    'rest_framework.authtoken',
    'common.apps.CommonConfig',
    'website.apps.WebsiteConfig',
    'database.apps.DatabaseConfig',
    'webdav.apps.WebdavConfig',
    'ftpserver.apps.FtpserverConfig',
    'terminal.apps.TerminalConfig'
]

SPECTACULAR_SETTINGS = spectacular.SPECTACULAR_DEFAULTS

MIDDLEWARE = [
    'base.middleware.PerformanceStatistics',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'base.pagination.LargeResultsSetPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'EXCEPTION_HANDLER': 'base.exception.base_exception_handler',
    'PAGE_SIZE': 5,
    'NON_FIELD_ERRORS_KEY': 'message'

}

CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = config('CELERY_ACCEPT_CONTENT', cast=lambda v: [s.strip() for s in v.split(',')])
CELERY_TASK_SERIALIZER = config('CELERY_TASK_SERIALIZER')
CELERY_RESULT_SERIALIZER = config('CELERY_RESULT_SERIALIZER')
CELERY_TIMEZONE = config('CELERY_TIMEZONE')

ROOT_URLCONF = 'UISSH.urls'
WSGI_APPLICATION = 'UISSH.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(str(BASE_DIR), 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_CONFIG = {'ENGINE': config('DJANGO_DATABASE_ENGINE')}

if DATABASE_CONFIG['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASE_CONFIG['NAME'] = os.path.join(BASE_DIR, 'db.sqlite3')
else:
    DATABASE_CONFIG.update({
        'NAME': config('DJANGO_DATABASE_NAME'),
        'CONN_MAX_AGE': 3,  # 60秒
        'USER': config('DJANGO_DATABASE_USER'),
        'PASSWORD': config('DJANGO_DATABASE_PASSWORD'),
        'HOST': config('DJANGO_DATABASE_HOST'),
        'PORT': config('DJANGO_DATABASE_PORT', default=3306, cast=int),
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    })

DATABASES = {
    'default': DATABASE_CONFIG
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='Asia/Shanghai', cast=str)

USE_I18N = config('USE_I18N', default=True, cast=bool)

USE_L10N = config('USE_L10N', default=True, cast=bool)

USE_TZ = config('USE_TZ', default=True, cast=bool)

# Django 3.2 要求
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/gg_django_cache',
    }
}
