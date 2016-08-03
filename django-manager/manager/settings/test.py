from .dev import *


# disabling loggers
del LOGGING['loggers']

# Django REST Framework defaults to JSON requests
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
