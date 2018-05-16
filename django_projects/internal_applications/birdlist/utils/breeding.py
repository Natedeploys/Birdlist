from birdlist.models import Cage, Bird, Coupling
from birdlist.utils.bird import get_juveniles, find_available_good_previous_couples, find_birds_for_breeding


def check_coupling_links():
    '''
    alert user if brood coupling is different from current cage couple
    '''

    breeding_cages = Cage.objects.filter(function=Cage.FUNCTION_BREEDING)
    c = get_juveniles()

    for i in breeding_cages:
        birds_in_cage = Bird.objects.filter(cage = i)
        juveniles_in_cage = birds_in_cage.filter(id__in = c)
        coupling = Coupling.objects.filter(cage = i, separation_date=None)
        coupling_id = ''
        if coupling:
            coupling_id = coupling.get().id
        for j in juveniles_in_cage:
            if j.brood.coupling.id != coupling_id:
                print "problem in cage %s:" %i.name
                print "couple coupling id = %s"  % coupling_id
                print "brood  coupling id = %s" % j.brood.coupling.id
                
                
def sort_birds_for_breeding(couples, males, females, GET):

    dummy_age = 10000
    sort_by = ''

    if GET.has_key('sort'):
        sort_by = GET['sort']    
    
        # sort by name(s)
        if sort_by in ('name', 'male', 'female'):
            if sort_by in ('name', 'male'):
                couples = sorted(couples, key=lambda k: k['male'].name)
            else:
                couples = sorted(couples, key=lambda k: k['female'].name)                

            males = sorted(males, key=lambda k: k['bird'].name)
            females = sorted(females, key=lambda k: k['bird'].name)
            
        # sort by cage name(s)
        elif sort_by in ('cage', 'female_cage', 'male_cage'):
            if sort_by in ('cage', 'male_cage'):
                couples = sorted(couples, key=lambda k: k['male_cage'])
            else:
                couples = sorted(couples, key=lambda k: k['female_cage'])
            males = sorted(males, key=lambda k: k['bird'].cage.name)
            females = sorted(females, key=lambda k: k['bird'].cage.name)
            
        # sort by age(s)            
        elif sort_by in ('age', 'male_age', 'female_age'):
            if sort_by in ('age', 'male_age'):
                couples = sorted(couples, key=lambda k: int(k['male_age'] or dummy_age))
            else:
                couples = sorted(couples, key=lambda k: int(k['female_age'] or dummy_age))
                
            males = sorted(males, key=lambda k: int(k['age'] or dummy_age))
            females = sorted(females, key=lambda k: int(k['age'] or dummy_age))

        # sort by AvgNoBroods
        elif sort_by == 'broods':
            couples = sorted(couples, key=lambda k: k['AvgNoBroods'])
            
        # sort by AvgNoJuvs            
        elif sort_by == 'juveniles':
            couples = sorted(couples, key=lambda k: k['AvgNoJuvs'])
    
    return couples, males, females, sort_by
    

def get_birds_for_breeding(session, exact_method):
    ''' 
        get list of couples, males, etc. - use previously generated data if 
        available
    '''

    recompute = False
    # check if birds_for_breeding has been computed previously
    if not session.has_key('birds_for_breeding'):
        # not found -> compute
        recompute = True
    else:
        # found -> check if method is the same
        birds_for_breeding = session['birds_for_breeding']
        method = birds_for_breeding['method']
        if method != exact_method:
            # method changed -> recompute
            recompute = True
        else:
            # method is the same -> get the previous results if list of males
            # and females didn't change
            males_qs, females_qs = find_birds_for_breeding(use_exact_method = exact_method)
            males_id = birds_for_breeding['males_id']
            females_id = birds_for_breeding['females_id']
            if males_id != list(males_qs.values_list('id', flat = True)) or females_id != list(females_qs.values_list('id', flat = True)):
                # males or females changed -> recompute
                recompute = True

    if recompute == True:
        couples, males, females, males_id, females_id = find_available_good_previous_couples(use_exact_method=exact_method)
    else:
        couples = birds_for_breeding['couples']
        males = birds_for_breeding['males']
        females = birds_for_breeding['females']

    return couples, males, females, males_id, females_id
    
    
