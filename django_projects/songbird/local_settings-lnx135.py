
BASE_URL = 'django/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/ubu135/django/django_templates"
)

# use gmail to send emails locally
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'songbirddebug@gmail.com'
EMAIL_HOST_PASSWORD = 'bla1bla2bla3'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = (
    ('Andreas Kotowicz', 'andreas.kotowicz@gmail.com'),
)

MANAGERS = ADMINS
