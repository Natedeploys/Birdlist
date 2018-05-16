from django.views.generic.simple import direct_to_template

from birdlist.models import Coupling
from birdlist.utils.breeding import sort_birds_for_breeding, get_birds_for_breeding

'''
def current_couples_print(request):
    #
    #
    # the current couples
    couplings = Coupling.objects.filter(separation_date=None).select_related().order_by('cage__name')
    return direct_to_template(request, "birdlist/print/print_couples.html",\
            { 'couplings': couplings, })
'''            
            
# /breeding/birds_for_breeding/ and /breeding/birds_for_breeding_exact/
def birds_for_breeding(request, exact_method = False):
    '''
    '''
    
    # get list of couples, males, etc. - use previously generated data if available
    couples, males, females, males_id, females_id = get_birds_for_breeding(request.session, exact_method)
    
    # do the sorting
    couples, males, females, sort_by = sort_birds_for_breeding(couples, males, females, request.GET)
    
    # dict for template
    var_dict = { 'couples': couples, 'females': females, 'males': males, 
                 'method': exact_method, 'sort_by': sort_by, 
                 'males_id': males_id, 'females_id': females_id, }
    
    # save dict in session so we can reuse the results
    request.session['birds_for_breeding'] = var_dict
    
    return direct_to_template(request, 'birdlist/birds_for_breeding.html', 
                                        extra_context = var_dict)


