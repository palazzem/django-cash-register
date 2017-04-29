import os
import dj_database_url

from getenv import env


# django-manager is the root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(BASE_DIR, '..')

# security
SECRET_KEY = env('DJANGO_SECRET_KEY')

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

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', '').replace(' ', '').split(',')

DEBUG = env('DJANGO_DEBUG', False)

# apps and middleware
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'djmoney',
    'rest_framework',

    # current application
    'registers',

    # TODO: interactive POS is disable because incomplete
    # 'pos',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'manager.wsgi.application'

# database configuration
DATABASES_DEFAULT = 'postgres://devel:123456@127.0.0.1:5432/cashregister'
DATABASES = {
    'default': dj_database_url.config(default=DATABASES_DEFAULT),
}

# use in-memory cache because it's not a high traffic service
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'django-cash',
    }
}

# internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# only one currency at a time is supported;
# if you want to support different currencies, the
# application design must be updated
CURRENCIES = ('EUR',)

# list of Adapters that are used to push data to third party services
# Available adapters are:
#   * 'registers.adapters.printers.CashRegisterAdapter'
PUSH_ADAPTERS = [
    'registers.adapters.services.DatadogAdapter',
]

# Datadog adapter settings
DATADOG_API_KEY = env('DJANGO_DATADOG_API_KEY', None)

# cash register settings
REGISTER_NAME = env('DJANGO_REGISTER_NAME', 'Shop')
SERIAL_PORT = env('DJANGO_SERIAL_PORT', '/dev/ttyUSB0')
SERIAL_BAUDRATE = env('DJANGO_SERIAL_BAUDRATE', 9600)
SERIAL_XONXOFF = env('DJANGO_SERIAL_XONXOFF', True)
SERIAL_TIMEOUT = env('DJANGO_SERIAL_TIMEOUT', 1)

# static files and media
ASSETS_ROOT = env('DJANGO_ASSETS_ROOT', BASE_DIR)
STATIC_HOST = env('DJANGO_STATIC_HOST', '')

STATIC_URL = STATIC_HOST + '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(ASSETS_ROOT, 'static')
MEDIA_ROOT = os.path.join(ASSETS_ROOT, 'media')

# emails
DEFAULT_FROM_EMAIL = env('DJANGO_FROM_EMAIL')
EMAIL_BACKEND_DEFAULT = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', EMAIL_BACKEND_DEFAULT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s [%(process)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(message)s'
        },
        'syslog': {
            'format': '%(levelname)s %(name)s [%(process)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'syslog',
        },
    },
}
