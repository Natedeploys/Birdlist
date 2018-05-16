# where's the media data stored locally?
MEDIA_ROOT = '/media/daten/HahnloserLab/django-birdy/local-media-root'
DATABASE_PASSWORD = 'adeft1ft'
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/media/daten/HahnloserLab/django-birdy/code/django/django_templates"
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Joergen Kornfeld', 'joergen.kornfeld@gmail.com '),
)

MANAGERS = ADMINS

