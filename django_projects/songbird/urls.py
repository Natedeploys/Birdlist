 #
from django.conf.urls.defaults import *
from django.conf import settings

# custom 404 and 500 error handlers, must be specified here, and not inside the 
# songbird_urls file.
handler404 = 'songbird.views.generic_page_not_found'
handler500 = 'songbird.views.generic_server_error'

urlpatterns = patterns(
    '',
    (r'^%s' % settings.BASE_URL, include('songbird.songbird_urls')),
)


# starting with django 1.3
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

## for the development server we need to remap the MEDIA_* directories 
# but no STATIC_URL.
import sys
import settings
if 'runserver' in sys.argv:
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)$' % (settings.MEDIA_URL[1:]), 'serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^%s(?P<path>.*)$' % (settings.LABLOG_MEDIA[1:]), 'serve', {'document_root': settings.LABLOG_MEDIA}),
        (r'^%s(.*)$' % (settings.ADMIN_MEDIA_PREFIX[1:]), 'serve', {'document_root' : settings.ADMIN_MEDIA_PATH_RELATIVE_TO_PROJECT, 'show_indexes' : True}),
    )
