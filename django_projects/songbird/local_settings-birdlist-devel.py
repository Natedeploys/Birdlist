# local_settings-birdlist-devel.py

DEBUG = False 
TEMPLATE_DEBUG = False 

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'songbird',
        'USER': 'songbird',
        'PASSWORD': 'songbird',
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    },
}

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/songbird/src/birdlist/django_templates"
)

# Do not spam from development
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = '[songbird-devel] '
DEFAULT_FROM_EMAIL = 'webmaster@songbird-devel.lan.ini.uzh.ch'

