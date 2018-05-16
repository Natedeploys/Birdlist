from django.conf.urls.defaults import *

# Remember 1:
# Don't name the views file like the application or a model - otherwise you'll
# get namespace problems and it will take you ages to debug them!!

# Remember 2:
# If you change the name for any of the view functions, it might be necessary to
# delete all *.pyc files from the PROJECT directory.

################################################################################


################################################################################

## main /lablog/username/ url ##################################################
urlpatterns = patterns('lablog.views.basic.lablog_main',
    url(r'^$', 'index_user', {}, 'index_user'),
    url(r'^tags/$', 'show_user_tags', {}, 'show_user_tags'),    
    url(r'^tags/(?P<tag>[^/]+)/$', 'show_user_tags', {}, 'show_user_tags'),
    url(r'^help/$', 'index_help', {}, 'index_help'),      
    ## create new objects with pop-up button
    url(r'^experiment/popup/new/$', 'popup_new_Experiment', {}, 'popup_new_Experiment'),
    url(r'^project/popup/new/$', 'popup_new_Project', {}, 'popup_new_Project'),
    url(r'^protocol/popup/new/$', 'popup_new_Protocol', {}, 'popup_new_Protocol'),
    url(r'^xhr_test/(?P<format>\w+)/$', 'xhr_test', {}, 'xhr_test'),
)

################################################################################
## do not use generic views because you can not filter the queryset! ###########
################################################################################



################################################################################
""" /lablog/username/collaborations/ and anything below it """

urlpatterns += patterns('lablog.views.collaboration.collaboration_main',
    url(r'^collaboration/$', 'index', {}, 'index_collaboration'),
)


################################################################################
""" /lablog/username/experiments/ and anything below it """

urlpatterns += patterns('lablog.views.experiment.experiment_main',
    url(r'^experiment/$', 'index', {}, 'index_experiment'),
    url(r'^experiment/new/$', 'new_experiment_with_bird', {}, 'new_experiment'),
    url(r'^experiment/possible_imports_from_animal_list/$', 'possible_imports_from_animal_list', {}, 'possible_imports_from_animal_list'),    
    url(r'^experiment/import_from_animal_list/$', 'import_from_animal_list', {}, 'import_from_animal_list'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/merge_experiment_with_animal_list/$', 'merge_experiment_with_animal_list', {}, 'merge_experiment_with_animal_list'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/$', 'detail', {}, 'detail_experiment'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/generic/$', 'detail_generic', {}, 'detail_generic'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/search/$', 'search', {}, 'search_experiment'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/$', 'list_events', {}, 'list_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/(?P<entries_per_page>\d+)/$', 'list_events', {}, 'list_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<year>\d{4})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<year>\d{4})/(?P<month>\d{2})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<event_type_id>\d+)/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<event_type_id>\d+)/(?P<year>\d{4})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<event_type_id>\d+)/(?P<year>\d{4})/(?P<month>\d{2})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/all/(?P<event_type_id>\d+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'list_all_events', {}, 'list_all_events'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/between/$', 'list_events_between_start', {}, 'list_events_between_start'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/list/between/(?P<event_type_id>\d+)/$', 'list_events_between', {}, 'list_events_between'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/edit/$', 'edit_form', {}, 'edit_experiment'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/delete/$', 'delete', {}, 'delete_experiment'),
)

############### EVENT TYPES OF THIS EXPERIMENT #################################
urlpatterns += patterns('lablog.views.event_type.event_type_main',
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/event_type/$', 'index', {}, 'index_event_type'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/event_type/(?P<entries_per_page>\d+)/$', 'index', {}, 'index_event_type'),
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/event_type/(?P<event_type_id>\d+)/delete/$', 'delete', {}, 'delete_event_type'),
)

############## ADDITIONAL EVENT TYPE FUNCTIONS #################################
urlpatterns += patterns('lablog.views.event_type.event_type_main',
    url(r'^experiment/(?P<experiment_slug>[-\w]+)/event_type/(?P<event_type_id>\d+)/edit/$', 'edit', {}, 'edit_EventType'),
    url(r'^event_type/$', 'redirect_index', {}, 'redirect_index_event_type'),
    url(r'^event_type/popup/new/$', 'popup_new_EventType', {}, 'popup_new_EventType'),
    url(r'^event_type/popup/(?P<event_type_id>\d+)/edit/$', 'popup_edit_EventType', {}, 'popup_edit_EventType'),
)

################################################################################
urlpatterns += patterns('lablog.views.event.event_main',
    url(r'^event/$', 'index', {}, 'index_event'),
    url(r'^event/new/$', 'new', {}, 'new_event_no_experiment'),    
    url(r'^event/new/(?P<experiment_id>[-\w]+)/$', 'new', {}, 'new_event'),
    url(r'^event/(?P<event_id>\d+)/$', 'detail', {}, 'detail_event'),
    url(r'^event/(?P<event_id>[-\w]+)/edit/$', 'edit_form', {}, 'edit_event'),
    url(r'^event/(?P<event_id>[-\w]+)/delete/$', 'delete', {}, 'delete_event'),
    url(r'^event/(?P<event_id>[-\w]+)/tag/$', 'tag', {}, 'tag_event'),
    url(r'^event/(?P<event_id>[-\w]+)/tag/(?P<tag_id>\d+)/delete/$', 'delete_tag', {}, 'tag_event_delete'),    
)


################################################################################
""" /lablog/username/projects/ and anything below it """

urlpatterns += patterns('lablog.views.project.project_main',
    url(r'^project/$', 'index', {}, 'index_project'),
    url(r'^project/new/$', 'new', {}, 'new_project'),
    url(r'^project/(?P<project_id>\d+)/$', 'lookup', {}, 'lookup_project'),
    url(r'^project/(?P<project_slug>[-\w]+)/$', 'detail', {}, 'detail_project'),
    url(r'^project/(?P<project_slug>[-\w]+)/edit/$', 'edit_form', {}, 'edit_project'),
    url(r'^project/(?P<project_slug>[-\w]+)/delete/$', 'delete', {}, 'delete_project'),
    url(r'^project/(?P<project_slug>[-\w]+)/search/$', 'search', {}, 'search_project'),
)


################################################################################
urlpatterns += patterns('lablog.views.note.note_main',
    url(r'^note/$', 'index', {}, 'index_note'),
    url(r'^note/new/$', 'new', {}, 'new_note_no_project'),    
    url(r'^note/new/(?P<project_id>[-\w]+)/$', 'new', {}, 'new_note'),
    url(r'^note/(?P<note_id>\d+)/$', 'detail', {}, 'detail_note'),
    url(r'^note/(?P<note_id>[-\w]+)/edit/$', 'edit_form', {}, 'edit_note'),
    url(r'^note/(?P<note_id>[-\w]+)/delete/$', 'delete', {}, 'delete_note'),
)


################################################################################
""" /lablog/username/protocols/ and anything below it """

urlpatterns += patterns('lablog.views.protocol.protocol_main',
    url(r'^protocol/$', 'index', {}, 'index_protocol'),
    url(r'^protocol/new/$', 'new', {}, 'new_protocol'),            
    url(r'^protocol/(?P<protocol_slug>[-\w]+)/$', 'detail', {}, 'detail_protocol'),      
    url(r'^protocol/(?P<protocol_slug>[-\w]+)/edit/$', 'edit_form', {}, 'edit_protocol'),
    url(r'^protocol/(?P<protocol_slug>[-\w]+)/delete/$', 'delete', {}, 'delete_protocol'),         
)

################################################################################
""" /lablog/username/external_view/ and anything below it """

urlpatterns += patterns('lablog.views.externalview.externalview_main',
    # This is a demo for view only urls - don't require authentication by default
    url(r'^external_view/$', 'index', {}, 'external_views'),
)

################################################################################
""" /lablog/username/rtm/ and anything below it """

urlpatterns += patterns('lablog.views.rtm.rtm_main',
    # This is a demo for view only urls - don't require authentication by default
    url(r'^rtm/$', 'index', {}, 'index_rtm'),
    url(r'^rtm/auth/$', 'authenticate', {}, 'rtm_auth'),    
    url(r'^rtm/browse/$', 'browse', {}, 'rtm_browse'),    
)



################################################################################
## debug pattern. use it in the django shell like this: #########################
#urlpatterns += patterns('',
#    url(r'^(\w+)/$', lambda: 0, 'asdf'),
#)

#  from django.core.urlresolvers import reverse
# reverse('detail_project', args=['foo', 'bar'])
# reverse('detail_project', args=['foo']) -> will raise error! number of arguments
# is important

