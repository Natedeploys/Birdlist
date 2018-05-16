# Django settings for songbird project.

''' DJANGO 1.3 TODO:


 1. migrate function-based generic views:
    https://docs.djangoproject.com/en/1.3/topics/generic-views-migration/
 
 
 2. find deprecated calls on develserver: $ python -W error  manage.py runserver
 
 
 3. understand why I keep getting this error on the ubuntu 10.10 server:
 
     /home/db/django/libraries/lib/python/django/core/context_processors.py:27: 
     DeprecationWarning: The context processor at `django.core.context_processors.auth` 
     is deprecated; use the path `django.contrib.auth.context_processors.auth` instead.
      DeprecationWarning
      
    /home/db/django/libraries/lib/python/django/template/loaders/filesystem.py:58: 
    DeprecationWarning: 'django.template.loaders.filesystem.load_template_source' is 
    deprecated; use 'django.template.loaders.filesystem.Loader' instead.
      DeprecationWarning
      
    /home/db/django/libraries/lib/python/django/template/loaders/app_directories.py:71: 
    DeprecationWarning: 'django.template.loaders.app_directories.load_template_source' 
    is deprecated; use 'django.template.loaders.app_directories.Loader' instead.
      DeprecationWarning

'''


''' 
    for list of all settings see, 
    https://docs.djangoproject.com/en/1.3/ref/settings/
'''


# do not show debug messages on real server
DEBUG = True
TEMPLATE_DEBUG = False 

''' 
A tuple that lists people who get code error notifications. When DEBUG=False and 
a view raises an exception, Django will e-mail these people with the full 
exception information. Each member of the tuple should be a tuple of 
(Full name, e-mail address).
'''
ADMINS = (
    ('Andreas Kotowicz', 'andreas.kotowicz@gmail.com'),
    ('Michael Graber', 'michael@ini.phys.ethz.ch'),
)

'''
A tuple in the same format as ADMINS that specifies who should get broken-link 
notifications when SEND_BROKEN_LINK_EMAILS=True.
'''
MANAGERS = ADMINS

'''
Whether to send an e-mail to the MANAGERS each time somebody visits a 
Django-powered page that is 404ed with a non-empty referer (i.e., a broken link). 
This is only used if CommonMiddleware is installed (see Middleware. See also 
IGNORABLE_404_STARTS, IGNORABLE_404_ENDS and Error reporting via e-mail.
'''
SEND_BROKEN_LINK_EMAILS = True


'''
A dictionary containing the settings for all databases to be used with Django. 
It is a nested dictionary whose contents maps database aliases to a dictionary 
containing the options for an individual database.
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'django',             # Or path to database file if using sqlite3.
        'USER': 'root',             # Not used with sqlite3.
        'PASSWORD': 'django_pass',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    },
}



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# if you want to use a different base url than "/" add it here, e.g.:
#BASE_URL = 'django/' # without leadning "/"!
BASE_URL = ''


# in django > 1.3, this is where the uploaded media files go to.
MEDIA_ROOT = '/var/www/media/'
MEDIA_URL = '/media/'
# look for further MEDIA_URL references.
# grep "MEDIA_URL" -R *|grep -v .pyc | more



# see https://docs.djangoproject.com/en/1.3/howto/static-files/#upgrading-from-django-staticfiles
# in django > 1.3, this is where the static files (images, CSS, Javascript, etc.) 
# go to. In the templates, we'll need to replace all 'MEDIA_URL' with 'STATIC_URL'
STATIC_URL = '/static/'
# point to the filesystem path you'd like your static files collected to when 
# you use the collectstatic management command. 
STATIC_ROOT = '/var/www/static/'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # "/home/db/django/django_templates",
    "/Users/jonathanprada/Documents/GitHub/Birdlist/django_templates"
)


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# refer to 'ADMIN_MEDIA_PREFIX' in templates via '{{ admin_media_url }}'
# also don't forget to use this path inside the CSS files.
ADMIN_MEDIA_PREFIX = '/admin-media/'
ADMIN_MEDIA_PATH_RELATIVE_TO_PROJECT = '../../libraries/lib/python/django/contrib/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0qoj797q$+cv)b2cfia&j(gwv)l*97)n-&%y_4noo^8%tk+vgo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # this middleware might (sometimes) cause problems see its documentation
    'middleware.StripWhitespaceMiddleware.StripWhitespaceMiddleware',
    'middleware.authentication_required.AuthenticationRequiredMiddleware',
    'middleware.check_user_permissions.UserOwnsDirectoryMiddleware',
    # debug toolbar - activated by default on the devel server
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

################################################################################
# for debugging django
# see also: http://simonwillison.net/2008/May/22/debugging/

# needed for django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1',)


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'HIDE_DJANGO_SQL': False,
    'TAG': 'div',
}


# log information to the django devel server console
import logging
#level = logging.DEBUG
#level = logging.INFO
level = logging.WARNING
logger = logging.getLogger('django')   # Django's catch-all logger
hdlr = logging.StreamHandler()  # Logs to stderr by default
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(level)

# or:
#logging.basicConfig(
#    level = logging.DEBUG,
#    format = '%(asctime)s %(levelname)s %(message)s',
#)



# usage:
# import logging
# logging.debug("this is a debug message")


################################################################################
# use INI's email server so we can send out emails to external addresses 

EMAIL_HOST = 'smtp.ini.uzh.ch'
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = '[zongbird-db] '
DEFAULT_FROM_EMAIL = 'webmaster@zongbird-db.lan.ini.uzh.ch'

################################################################################

# django authentication parameters
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 600 # user session should expire after 10 minutes of inactivity
SESSION_SAVE_EVERY_REQUEST = True # update the cookie at every request, otherwise you get logged out after 10 minutes - independent of the activity


# how many days is the activation code (provided through /accounts/register) valid?
# after this number of days, the code will expire.
ACCOUNT_ACTIVATION_DAYS = 3

ROOT_URLCONF = 'songbird.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.flatpages',
    # not used anymore; AK - 2011-01-08
    #'django.contrib.databrowse',
    'django.contrib.humanize',
    'django.contrib.markup',
    # starting with django 1.3
    'django.contrib.staticfiles',

    # internal applications first 
    # songbird needs to be added, otherwise the 'static' files won't be seen.
    'songbird',
    'lablog',
    'birdlist',
    'importexport',

    # external applications    
    'debug_toolbar',            # 2011/06/11 - updated to 0f4e780ebefe2a136f0bf97217c2ee6758cddf26, which is post version 0.8.5
    'django_evolution',         # 2011/06/11 - updated to SVN r205 = 0.6.3
    'helpdesk',                 # 2011/06/11 - updated to commit 9cad876f71df364c50cf
    'registration',             # 2011/01/08 - updated to version 0.8 alpha1 (released Mar 21, 2010), modified for songbird, checked for new version, 2011/06/11
    'sorl.thumbnail',           # 2011/01/04 - updated to version 3.2.5, checked for new version, 2011/06/11
    'tagging',                  # 2011/01/02 - updated to version 0.3.1, checked for new version, 2011/06/11
    'tagging_autocomplete',     # 2011/01/02 - updated to version 0.3.1   
    'autocomplete',             # 2011/01/10 - installed version 'tip' from 2010/09/12, ~ version 0.2
    #'pastebin',                   # 2011/01/13 - installed version 6080861aa91f05bc4fbadeb87d75068b8b179bc3 (2 commits post 0.2.4)
    #'mptt',                     # 2011/01/13 - installed version 0.4.2
    
    # not used anymore; AK - 2011-01-08 
    #'todo',                     # 2009/01/31 - installed version 0.9.5    
    
    # not used anymore; AK - 2011-01-08 
    # - filebrowser             # 2009/09/22 - installed SVN r204
    
    # libraries
    # - RememberTheMilk         # 2010/12/19 - installed version from http://anticube.blogspot.com/2008/01/remember-milk-api-python-wrapper.html
    # this is a library that needs to be registered like an app because of its 'charts' templatetag
    'GChartWrapper.charts',     # 2009/11/19 - installed version 0.9, checked on 2011/01/08, this is the latest version
)

MYSQLDUMP = "/usr/bin/mysqldump"


BATCHADMIN_MEDIA_PREFIX = "batchadmin/"
BATCHADMIN_JQUERY_JS = BATCHADMIN_MEDIA_PREFIX + "js/jquery.js"

TAGGING_AUTOCOMPLETE_JS_BASE_URL = "/static/songbird/js"
TAGGING_AUTOCOMPLETE_CSS_BASE_URL = "/static/songbird/css"


# make context processors available in templates
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    # starting with django 1.3
    'django.core.context_processors.static',
    #    
    'songbird.context_processors.base_url',
    #'lablog.context_processors.login_url',
    'lablog.context_processors.logout_url',
    'lablog.context_processors.admin_media_url',
    'lablog.context_processors.lablog_media_url',
    'birdlist.context_processors.birdlist_login_url',
    'birdlist.context_processors.birdlist_logout_url',    
    'todo.context_processors.todo_vars',
)


# This assumes you're serving static media from /site_media
TODO_MEDIA_URL = '/media/todo/'

# default redirection is to /lablog/
LOGIN_REDIRECT_URL = '/%sbirdlist/' % BASE_URL
# birdlist specific login / logout points
LOGIN_URL_BIRDLIST = '/%sbirdlist/login/' % BASE_URL
LOGOUT_URL_BIRDLIST = '/%sbirdlist/logout/' % BASE_URL
# lablog specific login / logout points
LOGIN_URL_LABLOG = '/%slablog/login/' % BASE_URL
LOGOUT_URL_LABLOG = '/%slablog/logout/' % BASE_URL

# specify where user authentication takes place
LOGIN_URL = LOGIN_URL_BIRDLIST
LOGOUT_URL = LOGOUT_URL_BIRDLIST


# which URLs need no authentication?
LOGIN_NOAUTH_URLS = (
    r'^$',
    r'^admin',
    r'^birdlist/xml',
    r'^lablog/external_view',
    r'^lablog/login', # needed so we can login directly at the birdlist url, otherwise we get redirected to /lablog/
    r'^lablog/logout',    
    r'^accounts',
    r'^todo',
    r'^helpdesk',
    r'^favicon\.ico',
    r'^%s' % (MEDIA_URL[1:]),
    r'^%s' % (STATIC_URL[1:]),
    r'^%s' % (ADMIN_MEDIA_PREFIX[1:]),
    r'^jsi18n',    
)

# which URLs require authentication?
LOGIN_REQUIREAUTH_URLS = (
    r'^lablog/$',
    r'^birdlist/$',
)

# where is the root folder that contains all media files?
LABLOG_MEDIA = "/mnt/projects/rich/"

# where is the folder on the webserver that shows to LABLOG_MEDIA?
LABLOG_MEDIA_URL = "lablog-media/"
THUMBNAIL_DEBUG = True
THUMBNAIL_PREFIX = "thumb_"
# where (on the webserver) do we generate the thumbnails?
THUMBNAIL_BASEDIR = LABLOG_MEDIA_URL + 'Temp/zongbird-db-thumbs/'

### load user / host specific settings if a file "local_settings" exists
try:
    from local_settings import *
except ImportError, exp:
    pass


# EOF

