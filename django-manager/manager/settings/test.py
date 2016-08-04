from .dev import *


# disabling loggers
del LOGGING['loggers']

# in-memory sqlite3 database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Django REST Framework defaults to JSON requests
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
