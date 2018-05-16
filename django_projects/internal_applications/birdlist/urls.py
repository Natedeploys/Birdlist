from django.conf.urls.defaults import *
import admin_filterspecs # so we can sort by alphabet in admin

## these need to come before all other patterns! ###########################
""" 
    /birdlist/logout 

    /birdlist/login is handled in birdlist_main    
    
"""

urlpatterns = patterns('',
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '../login'}, 'birdlistlogout'),
)

## the real birdlist urls come here ########################################

urlpatterns += patterns('birdlist.views.birdlist_main',
    url(r'^$', 'index', {}, 'index_birdlist'),
    url(r'^login/$', 'birdlistlogin', {}, 'birdlistlogin'),
    url(r'^search/$', 'search_database', {}, 'search_database'),    
    url(r'^birdcare/$', 'index_birdcare', {}, 'index_birdcare'),
    url(r'^breeding/$', 'index_breeding', {}, 'index_breeding'),
    ## create new objects with pop-up button
    url(r'^bird/popup/new/$', 'popup_new_bird', {}, 'popup_new_bird'),
    url(r'^cage/popup/new/$', 'popup_new_cage', {}, 'popup_new_cage'),
)

urlpatterns += patterns('birdlist.views.bird.bird_main',
    url(r'^bird/$', 'index', {}, 'index_bird'),
    url(r'^bird/tags/$', 'show_bird_tags', {}, 'show_bird_tags'),
    url(r'^bird/tags/(?P<tag>[^/]+)/$', 'show_bird_tags', {}, 'show_bird_tags'),
    url(r'^bird/list/$', 'list_all_birds', {}, 'list_all_birds'),
    url(r'^bird/alive/$', 'list_all_birds_alive', {}, 'list_all_birds_alive'),
    url(r'^bird/alive/(?P<species>[-\w]+)/$', 'list_all_birds_alive', {}, 'list_all_birds_alive'),
    url(r'^bird/alive/(?P<species>[-\w]+)/(?P<sex>[-\w]+)/$', 'list_all_birds_alive', {}, 'list_all_birds_alive'),
    url(r'^bird/alive/(?P<species>[-\w]+)/(?P<sex>[-\w]+)/(?P<cagetype>[-\w]+)/$', 'list_all_birds_alive', {}, 'list_all_birds_alive'),
    url(r'^bird/(?P<bird_id>\d+)/$', 'bird_overview', {}, 'bird_overview'),
    url(r'^bird/(?P<bird_id>\d+)/edit/$', 'bird_edit', {}, 'bird_edit'),
    url(r'^bird/(?P<bird_id>\d+)/transfer/$', 'transfer_bird_id', {}, 'transfer_bird_id'),
    url(r'^bird/(?P<bird_id>\d+)/sex/$', 'sex_bird_id', {}, 'sex_bird_id'),
    url(r'^bird/(?P<bird_id>\d+)/reserve/$', 'reserve_bird_id', {}, 'reserve_bird_id'),
    url(r'^bird/(?P<bird_id>\d+)/cancel_reservation/$', 'cancel_reserviation_bird_id', {}, 'cancel_reserviation_bird_id'),
    url(r'^bird/(?P<bird_id>\d+)/checkout_bird/$', 'checkout_bird', {}, 'checkout_bird'),
    url(r'^bird/(?P<bird_id>\d+)/test/$', 'test', {}, 'bird_test'),
    url(r'^bird/(?P<bird_id>\d+)/show_family_tree/$', 'show_family_tree', {}, 'show_family_tree'),
    url(r'^bird/show_juveniles/$', 'show_juveniles', {}, 'show_juveniles'),
    url(r'^bird/show_juveniles_by_age/$', 'show_juveniles_by_age', {}, 'show_juveniles_by_age'),
    url(r'^bird/show_adults/$', 'show_adults', {}, 'show_adults'),
    url(r'^bird/show_reservations_private/$', 'show_personal_reservations', {}, 'show_personal_reservations'),
    url(r'^bird/show_reservations/$', 'show_common_reservations', {}, 'show_common_reservations'),
    url(r'^bird/show_juveniles_breeding/$', 'show_juveniles_breeding', {}, 'show_juveniles_breeding'),
    url(r'^bird/catchbird/$', 'catch_bird', {}, 'catch_bird'),
)

''' not needed anymore
    url(r'^bird/create/$', 'create', {}, 'create_bird'),
    url(r'^bird/find/$', 'find', {}, 'find_bird'),
    url(r'^bird/transfer/$', 'transfer', {}, 'transfer_bird'),
    url(r'^bird/(?P<bird_id>\d+)/print/$', 'bird_print', {}, 'bird_print'),
'''    


urlpatterns += patterns('birdlist.views.activity.activity_main',
    url(r'^activity/$', 'index', {}, 'index_activity'),
    url(r'^activity/add_experiment/$', 'add_experiment', {}, 'add_experiment'),
    url(r'^activity/add_healthstatus/$', 'add_healthstatus', {}, 'add_healthstatus'),
    url(r'^activity/(?P<activity_id>\d+)/$', 'activity_detail', {}, 'activity_detail'),
    url(r'^activity/(?P<activity_id>\d+)/edit/$', 'activity_edit', {}, 'activity_edit'),
    url(r'^activity/(?P<activity_id>\d+)/close/$', 'activity_close', {}, 'activity_close'),
)

urlpatterns += patterns('birdlist.views.cage.cage_main',
    url(r'^cage/$', 'index', {}, 'index_cage'),
    url(r'^cage/show_cages_and_occupancy/$', 'index', {'occupancy': True, }, 'index_cage_with_occupancy'),
    url(r'^cage/by_function/$', 'index', {'by_function': True, }, 'index_cage_by_function'),
    url(r'^cage/cages_over_capacity/$', 'index', {'occupancy': True, 'over_capacity': True, }, 'cages_over_capacity'),
    url(r'^cage/gotocage/$', 'go_to_cage', {}, 'go_to_cage'),
    url(r'^cage/(?P<cagename>[-\w]+)/$', 'cage_overview', {}, 'cage_overview'),
    url(r'^cage/(?P<cagename>[-\w]+)/add_juveniles/$', 'add_juveniles_to_cage', {}, 'add_juveniles_to_cage'),
    url(r'^cage/(?P<cagename>[-\w]+)/add_couple/$', 'add_couple_to_cage', {}, 'add_couple_to_cage'),
    url(r'^cage/(?P<cagename>[-\w]+)/separate_couple/$', 'separate_couple', {}, 'separate_couple'),
    url(r'^cage/(?P<cagename>[-\w]+)/move_family/$', 'move_family', {}, 'move_family'),
    url(r'^cage/(?P<cagename>[-\w]+)/move_youngest_brood_and_mother/$', 'move_youngest_brood_and_mother', {}, 'move_youngest_brood_and_mother'),    
    url(r'^cage/(?P<cagename>[-\w]+)/edit_coupling_comment/$', 'edit_coupling_comment', {}, 'edit_coupling_comment'),
)

''' I don't think we use these anymore. AK, Jan 23rd 2011
url(r'^cage/show_all/$', 'show_all_cages', {}, 'show_all_cages'),
url(r'^cage/show_birds/$', 'show_birds_in_cage', {}, 'show_birds_in_cage'),
url(r'^cage/show_birds/(?P<cage_id>\d+)/$', 'show_birds_in_specific_cage', {}, 'show_birds_in_specific_cage'), 

'''



urlpatterns += patterns('birdlist.views.breeding.breeding_main',
    url(r'^breeding/birds_for_breeding/$', 'birds_for_breeding', {}, 'birds_for_breeding'),    
    url(r'^breeding/birds_for_breeding_exact/$', 'birds_for_breeding', {'exact_method': True }, 'birds_for_breeding_exact'),        
)

''' not used anymore, AK, Jan 23rd 2011
    url(r'^breeding/print/$', 'current_couples_print', {}, 'current_couples_print'),
'''    


urlpatterns += patterns('birdlist.views.breeding.birdcare_main',
    url(r'^birdcare/todo/$', 'birdcare_todo', {}, 'birdcare_todo'),
    url(r'^birdcare/cleanup/$', 'birdcare_db_cleanup', {}, 'birdcare_db_cleanup'),
)

''' not used anymore 
    url(r'^birdcare/checklist/$', 'birdcare_checklist', {}, 'birdcare_checklist'),
    url(r'^birdcare/checklist/print/$', 'print_birdcare_checklist', {}, 'print_birdcare_checklist'),
'''    


urlpatterns += patterns('birdlist.views.stats.stats_main',
    url(r'^stats/$', 'index', {}, 'index_stats'),
    url(r'^stats/nbr_couples_and_new_borns_per_week/$', 'nbr_couples_and_new_borns_per_week', {}, 'nbr_couples_and_new_borns_per_week'),
    url(r'^stats/nbr_animals_in_cage_per_week/$', 'nbr_animals_in_cage_per_week', {}, 'nbr_animals_in_cage_per_week'),
    url(r'^stats/all_animals_with_wrong_coupling_status/$', 'all_animals_with_wrong_coupling_status', {}, 'all_animals_with_wrong_coupling_status'),
    url(r'^stats/activities_by_user/$', 'show_activities_by_user', {}, 'show_activities_by_user'),
    url(r'^stats/show_activities_last_days/$', 'show_activities_last_days', {}, 'show_activities_last_days'),
    url(r'^stats/show_activities_last_days/(?P<how_many_days>\d+)/$', 'show_activities_last_days', {}, 'show_activities_last_x_days'),
    url(r'^stats/show_activities_timestamp_mismatch/$', 'show_activities_timestamp_mismatch', {}, 'show_activities_timestamp_mismatch'),
    url(r'^stats/my_experiments/$', 'show_my_experiments', {}, 'show_my_experiments'),
    url(r'^stats/experiments_by_licence/$', 'show_experiments_by_licence', {}, 'show_experiments_by_licence'),
    url(r'^stats/experiments_by_licence/(?P<year>\d{4})/$', 'show_experiments_by_licence', {}, 'show_experiments_by_licence'),
    url(r'^stats/experiments_without_licence/$', 'show_experiments_without_licence', {}, 'show_experiments_without_licence'),
    url(r'^stats/experiments_without_licence/(?P<year>\d{4})/$', 'show_experiments_without_licence', {}, 'show_experiments_without_licence'),
    url(r'^stats/experiments_by_user/$', 'show_experiments_by_user', {}, 'show_experiments_by_user'),
    url(r'^stats/experiments_by_bird/$', 'show_experiments_by_bird', {}, 'show_experiments_by_bird'),
    url(r'^stats/experiments_open/$', 'show_experiments_open', {}, 'show_experiments_open'),
    url(r'^stats/colony_overview/$', 'colony_overview_stats', {}, 'colony_overview_stats'),
)


''' pdf URLS '''
urlpatterns += patterns('birdlist.views.pdf.generate_sheets',
    url(r'^bird/(?P<bird_id>\d+)/pdf/$', 'bird_generate_pdf', {}, 'bird_generate_pdf'),
    url(r'^bird/(?P<bird_id>\d+)/generate_experiment_sheet/$', 'generate_exp_sheet', {'exp_id': None, }, 'generate_exp_sheet_no_title'),
    url(r'^bird/(?P<bird_id>\d+)/generate_experiment_sheet/(?P<exp_id>\d+)/$', 'generate_exp_sheet', {}, 'generate_exp_sheet'),
    url(r'^bird/show_reservations/pdf/$', 'show_common_reservations_pdf', {}, 'show_common_reservations_pdf'),
    url(r'^bird/show_juveniles_by_age/pdf/$', 'show_juveniles_by_age_pdf', {}, 'show_juveniles_by_age_pdf'),
    url(r'^breeding/pdf/$', 'current_couples_pdf', {}, 'current_couples_pdf'),
    url(r'^breeding/birds_for_breeding/pdf/$', 'birds_for_breeding_pdf', {}, 'birds_for_breeding_pdf'),    
    url(r'^breeding/birds_for_breeding_exact/pdf/$', 'birds_for_breeding_pdf', {'exact_method': True }, 'birds_for_breeding_exact_pdf'),      
    url(r'^cage/show_cages_and_occupancy/pdf/$', 'cages_with_occupancy_pdf', {}, 'cages_with_occupancy_pdf'),            
    url(r'^cage/(?P<cagename>[-\w]+)/pdf/$', 'show_birds_in_cage_pdf', {}, 'show_birds_in_cage_pdf'),
    url(r'^birdcare/worksheet/pdf/$', 'birdcare_worksheet', {}, 'birdcare_worksheet'),
)


''' xml URLS '''
urlpatterns += patterns('birdlist.views.xml.datadelivery',
    url(r'^xml/bird/(?P<birdname>[-\w]+)/$', 'bird_info', {}, 'bird_info'),
    url(r'^xml/bird/(?P<birdname>[-\w]+)/experiments/$', 'experiments_for_bird', {}, 'experiments_for_bird'),
)


urlpatterns += patterns('birdlist.views.help.help_main',
    url(r'^help/$', 'index', {}, 'index_help'),
)


# autocomplete stuff
from autocomplete.views import autocomplete
from birdlist.models import Activity, Bird, Cage
from birdlist.utils.bird import find_birds_for_breeding
queryset_male, queryset_female = find_birds_for_breeding()

autocomplete.register(
    id = 'birdname', 
    queryset = Bird.objects.all(),
    fields = ('name',),
    limit = 10,
)

autocomplete.register(
    id = 'cagename', 
    queryset = Cage.objects.all(),
    fields = ('name',),
    limit = 10,
)

autocomplete.register(
    id = 'used_cagename', 
    queryset = Cage.objects.exclude(function=Cage.FUNCTION_NOTUSEDANYMORE),
    fields = ('name',),
    limit = 10,
)

autocomplete.register(
    id = 'cage_for_separation', 
    queryset = Cage.objects.exclude(function__in = (Cage.FUNCTION_NOTUSEDANYMORE, Cage.FUNCTION_MISSING, Cage.FUNCTION_DISPOSAL)),
    fields = ('name',),
    limit = 10,
)

autocomplete.register(
    id = 'male_bird', 
    queryset = queryset_male,
    fields = ('name', ),
    limit = 10,
)

autocomplete.register(
    id = 'female_bird', 
    queryset = queryset_female,
    fields = ('name', ),
    limit = 10,
)

urlpatterns += patterns('',
    # If you want to use the same AutoComplete instance as a view for multiple
    # applications, you should register it only once in your project's URLconf.
    url(r'^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),
)

