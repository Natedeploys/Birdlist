
# where's the media data stored locally?
MEDIA_ROOT = '/local/tmp/django-media/'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/local/code/django/django_templates"
)


# setting DEBUG to False on devel server, will break static files!
# see: http://stackoverflow.com/questions/5343771/django-1-3-rc1-and-css
#
# staticfiles/urls.py:
#
# if settings.DEBUG and not urlpatterns:
#     urlpatterns += staticfiles_urlpatterns()
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Andreas Kotowicz', 'andreas.kotowicz@gmail.com'),
)
MANAGERS = ADMINS

MYSQLDUMP = "/usr/bin/mysqldump"

# where is the root folder that contains all media files?
LABLOG_MEDIA = "/local2/tmp/images"

# where is the folder on the webserver that shows to LABLOG_MEDIA?
LABLOG_MEDIA_URL = "lablog-media/"

# where (on the webserver) do we generate the thumbnails?
THUMBNAIL_BASEDIR = LABLOG_MEDIA_URL + 'db-thumbs/'

# use gmail to send emails locally
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'songbirddebug@gmail.com'
EMAIL_HOST_PASSWORD = 'bla1bla2bla3'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

