from django.conf.urls.defaults import *

# Remember 1:
# Don't name the views file like the application or a model - otherwise you'll
# get namespace problems and it will take you ages to debug them!!

# Remember 2:
# If you change the name for any of the view functions, it might be necessary to
# delete all *.pyc files from the PROJECT directory.

################################################################################
""" 

    /lablog/ 

    and
    
    /lablog/login
        
"""

urlpatterns = patterns('lablog.views.basic.lablog_main',
    url(r'^$', 'start', {}, 'index_lablog'),
    url(r'^login/$', 'labloglogin', {}, 'labloglogin'),
)

urlpatterns += patterns('lablog.views.basic',
    url(r'pdf/$', 'pdf.generate_dummy', {}, 'pdf_dummy'),
)

## these need to come before the /username/ pattern! ###########################
""" /lablog/logout """

urlpatterns += patterns('',
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '../'}, 'labloglogout'),
)

## main /lablog/username/ url ##################################################

urlpatterns += patterns('',
    (r'^(?P<username>[-\w]+)/', include('lablog.suburls')),
)

