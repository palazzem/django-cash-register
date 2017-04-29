from .base import *


# removing security enforcement in development mode
DEBUG = True
ALLOWED_HOSTS = ['localhost']
SECRET_KEY = env('DJANGO_SECRET_KEY', '1234567890')
INTERNAL_IPS = (
    '127.0.0.1',
)

# enabling console loggers
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'manager': {
        'handlers': ['console'],
        'level': env('MANAGER_LOG_LEVEL', 'DEBUG'),
    },
    'registers': {
        'handlers': ['console'],
        'level': env('MANAGER_LOG_LEVEL', 'DEBUG'),
    },
}
