#
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# django.databrowse enabling - # not used anymore; AK - 2011-01-08
# from django.contrib import databrowse

# settings.py file
from django.conf import settings

# our internal models
from lablog.models import Experiment, Project
from birdlist.models import Bird

# require login for databrowse
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    
    # this needs to be the topmost admin link!

    (r'^admin/import-export/', include('importexport.urls')),
    (r'^admin/accounts/', include('registration.backends.default.urls')),    

    # not used anymore; AK - 2011-01-08
    #(r'^admin/filebrowser/', include('filebrowser.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # enable the admin:
    # use this line if you have django 1.0
    #(r'^admin/(.*)', admin.site.root),
    # django 1.1
    (r'^admin/', include(admin.site.urls)),

    # not used anymore; AK - 2011-01-08
    #(r'^databrowse/(.*)', login_required(databrowse.site.root)),
        
    # external applications

    (r'^helpdesk/', include('helpdesk.urls')),
    # not used anymore; AK - 2011-01-08
    #(r'^todo/', include('todo.urls')),
    (r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
    (r'^ajax_filtered_fields/', include('ajax_filtered_fields.urls')),
    #(r'^mypaste/', include('pastebin.urls')),

    # internal applications
    (r'^lablog/', include('lablog.urls')),
    (r'^birdlist/', include('birdlist.urls')),

)


 
from django.views.generic.base import RedirectView
urlpatterns += patterns('',
    (r'^favicon\.ico$', RedirectView.as_view(url = '%s/songbird/favicon.ico' % (settings.STATIC_URL[:-1]))),
)

""" helper views """
urlpatterns += patterns('',
    (r'^keep_alive/$', 'songbird.views.keep_alive', {}, 'keep_alive'),
    (r'^nothing/$', 'songbird.views.nothing', {}, 'nothing'),      
    (r'^auto_logout/$', 'songbird.views.auto_logout', {}, 'auto_logout'),
)

""" create a default view for the / URL. Since apache has a different python 
    include path, we need to include the songbird. prefix """
urlpatterns += patterns('',
    (r'^$', 'songbird.views.start'),
)


## hijack django admin stuff  ##################################################
# see: http://groups.google.com/group/django-users/browse_thread/thread/b958a059b6dca44e/67cc4c2f05719a65?lnk=gst&q=admin+calendar&rnum=3
urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': 'django.conf'}),
)


