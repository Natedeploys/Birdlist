# use the "not_implemented" function to create blank views.
from lablog.views.basic.lablog_main import not_implemented, server_error
#def index(request):
#    return not_implemented(request, "externalview")

from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_index
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_detail

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.forms.util import ErrorList

import datetime

from birdlist.forms.birdlist_formsets import FindBirdForm, BirdForm, SelectCageForm, FindBirdsForNewCouple, ReserveBirdForm, CheckoutAnimalFromColonyForm
from birdlist.models import Bird, Cage, Activity, LabRoom, Activity_Type, Coupling
from birdlist.utils.bird import generate_qr_code, find_offspring, get_juveniles, get_adults, do_animal_transfer, find_birds_currently_breeding


def birdcare_todo(request):
    '''
    returns a list of things the person in charge of birdcare has to do
    '''
    # couples to separate and nests to be removed from
    couplings = Coupling.objects.filter(separation_date=None).select_related().order_by('cage__name')
    couples_to_separate = []
    remove_nests_from = []
    for coupling in couplings:
        if coupling.is_to_be_separated():
            couples_to_separate.append(coupling)
        if coupling.nest_has_to_be_removed():
            remove_nests_from.append(coupling)
            
    # juveniles to ring and transfer
    lower_datethreshold = datetime.date.today()-datetime.timedelta(60)
    juveniles = get_juveniles().filter(date_of_birth__lte=lower_datethreshold).filter(cage__function=Cage.FUNCTION_BREEDING)
    
    # empty breeding cages
    empty_breeding_cages = Cage.objects.get_empty_cages(function=Cage.FUNCTION_BREEDING)
     
    var_dict = { "couplings": couples_to_separate, "juveniles": juveniles, \
                "empty_breeding_cages": empty_breeding_cages, 'show_cage': True, \
                "remove_nests_from": remove_nests_from, }
    return direct_to_template(request, 'birdlist/birdcare_todo.html', var_dict)


def birdcare_db_cleanup(request):
    '''
    '''
    from birdlist.utils.database_maintenance import clean_up_db
    var_dict = { 'status_message' : clean_up_db(save=True) }

    return direct_to_template(request, 'birdlist/birdcare_db_cleanup.html', var_dict)


def get_checklist_information():
    '''
    gather all information about all breeding cages and output it 
    into a birdcare checklist
    '''
    cage_list = []

    breeding_cages = Cage.objects.filter(function=Cage.FUNCTION_BREEDING)

    for cage in breeding_cages:

        coupling = Coupling.objects.filter(cage=cage, separation_date=None)
        juveniles = None 

        if coupling:
            # it should not be possible that more than one coupling is 
            # in a cage
            coupling = coupling[0]
            broods = coupling.brood_set.all()
            juveniles = []
            for brood in broods:
                for juv in brood.bird_set.all():
                    if juv.cage == cage:
                        juveniles.append(juv)

        cage_dict = {
                    'cage': cage,
                    'coupling': coupling, 
                    'juveniles': juveniles,
                }
        
        cage_list.append(cage_dict)

    return cage_list

''' not used anymore
def birdcare_checklist(request):
    #
    # view for site
    #
    var_dict = { 'cage_list': get_checklist_information()}
    return direct_to_template(request, 'birdlist/birdcare_checklist.html', var_dict)


def print_birdcare_checklist(request):
    #
    # view for site
    #
    var_dict = { 'cage_list': get_checklist_information()}
    return direct_to_template(request, 'birdlist/print/print_birdcare_checklist.html', var_dict)
    
'''    
    
