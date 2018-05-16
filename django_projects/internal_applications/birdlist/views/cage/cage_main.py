# use the "not_implemented" function to create blank views.
# from lablog.views.basic.lablog_main import not_implemented
# def index(request):
#     return not_implemented(request, "externalview")

import datetime

from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from django import forms
from django.forms.util import ErrorList

from birdlist.forms.breeding_forms import EditCommentCouplingForm
from birdlist.models import Cage, Bird, Coupling, Brood, Couple, CoupleLookup
from birdlist.utils.bird import rename_juveniles
from birdlist.utils.cage import handle_new_juveniles, handle_new_couple, handle_couple_separation, mother_or_father_need_breeding_evaluation

def index(request, occupancy = None, by_function = None, over_capacity = None):
    '''
    '''
    if by_function:
        cages = Cage.objects.filter(function__lte = Cage.FUNCTION_SOCIAL).order_by('function', 'name').select_related()
    else:
        cages = Cage.objects.filter(function__lte = Cage.FUNCTION_SOCIAL).order_by('room', 'name').select_related()

    # exclude all cages where the occupancy is in the allowed limit.
    if over_capacity:
        exclude = []
        for i in cages:
            if i.occupancy() <= i.max_occupancy:
                exclude.append(i.id)
        cages = cages.exclude(id__in = exclude)
        
    var_dict = { 'cages': cages, }
    template = 'birdlist/cage_index.html'
    if occupancy or over_capacity:
        template = 'birdlist/cage_index_with_occupancy.html'
        if over_capacity:
            var_dict['title'] = 'Cages over capacity'
            var_dict['occupancy_link'] = 'True'
    if by_function:
        template = 'birdlist/cage_index_by_function.html'
        
    return direct_to_template(request, template, var_dict)


def cage_overview(request, cagename):
    ''' TODO: change code so that we pass on a dict instead of the bird objects.
              We currently waste most of the time doing lookups for birds, e.g.:
              'get_father', 'get_mother', 'get_mates_string'
    '''
    
    cage = get_object_or_404(Cage, name=cagename)

    if cage.function == cage.FUNCTION_BREEDING:
        birds_in_cage, missing_birds = get_birds_in_cage(cage)
        birds_in_cage = birds_in_cage.order_by('date_of_birth')
        show_mates = False
    else:
        birds_in_cage, missing_birds = get_birds_in_cage(cage)
        birds_in_cage = birds_in_cage.order_by('name')
        show_mates = True

    var_dict = {
            'cage': cage,
            'birds': birds_in_cage,
            'missingbirds': missing_birds,
            'show_do': True,
            'show_mates': show_mates,
            }

    return direct_to_template(request, 'birdlist/cage_overview.html',\
            var_dict)


def get_birds_in_cage(cageobject):
    '''
    '''
    birds = Bird.objects.filter(cage=cageobject)
    # separate missing birds
    missing_birds = birds.exclude(missing_since=None).order_by('name')
    birds_in_cage = birds.filter(missing_since=None)

    return birds_in_cage, missing_birds


'''
def show_all_cages(request):
    queryset = Cage.objects.all();
    # will use cage_list.html
    return object_list(request, queryset = queryset)
'''
'''
def show_birds_in_specific_cage(request, cage_id):
    return return_specific_cage(request, cage_id)
'''    
    
'''
def show_birds_in_cage(request, cage_id = None):
    from birdlist.forms.birdlist_formsets import SelectCageForm
    form = SelectCageForm();    
    if request.method == 'POST':
        cage_id = request.POST['cage']
        if cage_id:
            return HttpResponseRedirect(reverse('show_birds_in_specific_cage', args=(cage_id, )))

    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Select cage', 'form_object_name': 'cage', })
'''

'''
def return_specific_cage(request, cage_id):
    #this is a generic view - the 'bird_list.html' 
    #    template file will be used
    queryset = Bird.objects.filter(cage = cage_id);
    selected_cage = Cage.objects.get(pk = cage_id);
    header = 'All birds in cage ' + selected_cage.name
    img = generate_cage_usage_graph(cage_id)
    extra_context = {'header': header, 'img': img, }
    return object_list(request, queryset = queryset, extra_context = extra_context)
'''
'''
def nbr_birds_in_cage(cage_id):
    nbr_birds = Bird.objects.filter(cage__id =  cage_id).__len__()
    return nbr_birds
'''
'''
def generate_cage_usage_graph(cage_id):

    number_in_cage = nbr_birds_in_cage(cage_id)
    a = Cage.objects.get(pk = cage_id)
    max_allowed = a.max_occupancy.__int__()

    label1 = 'used'
    label2 = 'empty'
    data1 = number_in_cage
    data2 = max_allowed - number_in_cage
    if number_in_cage > max_allowed:
        data1 = number_in_cage - max_allowed
        data2 = max_allowed
        label1 = 'surplus'
        label2 = 'total allowed'

    from pygooglechart import PieChart3D
    # Create a chart object of 250x100 pixels
    chart = PieChart3D(350, 150)
    # Add some data
    chart.add_data([data1, data2])
    # Assign the labels to the pie data
    chart.set_pie_labels([label1, label2])
    chart.title = 'Todays cage utilization (empty vs filled cages)'
    # Print the chart URL
    a = chart.get_url()
    return 
'''

'''
def cage_print(request, cagename):
    #
    #
    cage = get_object_or_404(Cage, name=cagename)
    if cage.function == cage.FUNCTION_BREEDING:
        birds = Bird.objects.filter(cage=cage).order_by('date_of_birth')
    else:
        birds = Bird.objects.filter(cage=cage).order_by('name')

    return direct_to_template(request, 'birdlist/print/print_cage_birdlist.html',\
            {'cage': cage, 'birds': birds, })

'''




def add_juveniles_to_cage(request, cagename):
    '''
    '''
    from birdlist.forms.breeding_forms import AddJuvenilesForm

    cage = get_object_or_404(Cage, name=cagename)
    coupling = Coupling.objects.filter(cage=cage, separation_date=None)
    
    if cage.function == cage.FUNCTION_BREEDING:
        birds = Bird.objects.filter(cage=cage).order_by('date_of_birth')
    else:
        birds = Bird.objects.filter(cage=cage).order_by('name')

    if request.method == 'POST':
        form = AddJuvenilesForm(request.POST)

        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )

        if 'addbutton' in request.POST:
            if form.is_valid():
                JuvenileHandleError = handle_new_juveniles(form.cleaned_data['FirstBirthday'],\
                        form.cleaned_data['LastBirthday'],\
                        form.cleaned_data['NumberOfJuvenilesToAdd'], cage, coupling[0], request.user)

                if JuvenileHandleError:
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append(JuvenileHandleError)

                    var_dict = {'cage': cage, 'birds': birds, 'form_juvs': form, 'add':True, }
                    return direct_to_template(request,
                                'birdlist/cage_overview.html', var_dict)

                return HttpResponseRedirect(cage.get_absolute_url(), )

            else:
                var_dict = {'cage': cage, 'birds': birds, 'form_juvs': form, 'add':True, }
                return direct_to_template(request,
                            'birdlist/cage_overview.html', var_dict)

    else:
        whynotaddmessage = ''
        # check that there is not zero coupling
        nbr_couples = coupling.count()
        if nbr_couples == 0:
            whynotaddmessage = 'You cannot add a juvenile here because no couple was found in this cage.'
        # check that there is not more than one couplings
        elif nbr_couples > 1:
            whynotaddmessage = 'You cannot add a juvenile to this cage cause more than one couple was found in the db to be in this cage.'

        form = AddJuvenilesForm()
        var_dict = {'cage': cage,
                    'birds': birds,
                    'form_juvs': form,
                    'add':True,
                    'whynotaddmessage': whynotaddmessage,
                    }

        return direct_to_template(request, 'birdlist/cage_overview.html',\
            var_dict)
            


def add_couple_to_cage(request, cagename):
    '''
    '''
    from birdlist.forms.birdlist_formsets import FindBirdsForNewCouple

    cage = get_object_or_404(Cage, name=cagename)
    if cage.function == cage.FUNCTION_BREEDING:
        birds = Bird.objects.filter(cage=cage).order_by('date_of_birth')
    else:
        birds = Bird.objects.filter(cage=cage).order_by('name')

    if request.method == 'POST':
        form = FindBirdsForNewCouple(request.POST)
        
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )

        if 'addbutton' in request.POST:
            if form.is_valid():
                CoupleHandleError = handle_new_couple(form.cleaned_data['male'],\
                        form.cleaned_data['female'], form.cleaned_data['type'], \
                        cage, request.user)

                if CoupleHandleError:
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append(CoupleHandleError)

                    var_dict = {'cage': cage, 'birds': birds, 'form_couple': form, \
                                'add':True, }
                    return direct_to_template(request,
                                'birdlist/cage_overview.html', var_dict)
                
                return HttpResponseRedirect(cage.get_absolute_url(), )

            var_dict = { 'cage': cage, 'birds': birds, 'form_couple': form, \
                         'add': True, }
            return direct_to_template(request, 'birdlist/cage_overview.html',\
                var_dict)
    else:
        whynocouplemessage = ''
        # there is already a couple in this cage
        if Coupling.objects.filter(cage=cage, separation_date=None).count()!=0:
            whynocouplemessage = 'There is already a couple in this cage, you cannot add another one.'
        # cage function is not breeding 
        if cage.function != cage.FUNCTION_BREEDING:
            whynocouplemessage = 'This is not a breeding cage. You cannot add a couple here!'

        form = FindBirdsForNewCouple()
        var_dict = { 'cage': cage, 'birds': birds, 'form_couple': form, 'add': True, \
                    'whynocouplemessage': whynocouplemessage, }

        return direct_to_template(request, 'birdlist/cage_overview.html',\
               var_dict) 



def move_youngest_brood_and_mother(request, cagename):

    from birdlist.forms.birdlist_formsets import FindCageForBroodAndMotherMove, FindCageForBroodAndMotherMoveAskBreedingSuccess
    from birdlist.utils.bird import do_animal_transfer    

    cage = get_object_or_404(Cage, name=cagename)
    birds = Bird.objects.filter(cage=cage).order_by('name')
    couplings = Coupling.objects.filter(cage=cage, separation_date = None)
    
    if request.method == 'POST':
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )
        
        
        if 'movebutton' in request.POST:
            whynotmovemessage = ''
            
            # if user moved the family, goes 'back' in the browser and presses 
            # the 'move' button again, then couplings will be empty.
            try:
                coupling = couplings[0]
            except:
                return HttpResponseRedirect(cage.get_absolute_url(), )
                
            mother, father = coupling.couple.get_female_and_male()
            evaluate_breeding = False
            if mother_or_father_need_breeding_evaluation(mother, father, coupling) == True:
                form = FindCageForBroodAndMotherMoveAskBreedingSuccess(request.POST)
                evaluate_breeding = True
            else:
                form = FindCageForBroodAndMotherMove(request.POST)
                
            if form.is_valid():

                new_cage_id = request.POST['cage']
                new_cage = Cage.objects.get(pk = new_cage_id)
                
                if new_cage.occupancy() == 0:
                    
                    brood_present = False
                    # find youngest brood - will fail if no brood present
                    try:
                        youngest_brood_id = max(birds.exclude(name__in = (mother, father)).values_list('brood', flat = True))
                        youngest_brood_birds = birds.filter(brood__id = youngest_brood_id)
                        brood_present = True
                    except:
                        pass
                        
                    if brood_present == True:
                        # rename youngest brood 
                        rename_juveniles(youngest_brood_birds, cagename, new_cage.name)
                        # move birds
                        for i in youngest_brood_birds:
                            do_animal_transfer(i, new_cage_id, request.user)
                    
                    # move mother
                    do_animal_transfer(mother, new_cage_id, request.user)
                    
                    # separate couple
                    coupling.separation_date = datetime.date.today()
                    coupling.save()
                    
                    # flag animals according to breeding status (if given)
                    if evaluate_breeding == True:
                        breeder_status = request.POST['breeder_status']
                        mother.coupling_status = breeder_status
                        father.coupling_status = breeder_status
                        mother.save()
                        father.save()
                    
                    return HttpResponseRedirect(new_cage.get_absolute_url(), )
                
                else:
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append('Can not move brood & mother to non-empty cage.')

            var_dict = {'form_move_brood_with_mother': form, 'move': True, 
                    'whynotmovemessage': whynotmovemessage, 'cage': cage, 'birds': birds, }
            return direct_to_template(request, 'birdlist/cage_overview.html', var_dict)                
                
    
    else:
        nbr_couples = couplings.count()
        whynotmovemessage = ''
        if nbr_couples == 0:
            whynotmovemessage = 'There is no couple in this cage.'
            form = FindCageForBroodAndMotherMove()
        else:
            coupling = couplings[0]
            mother, father = coupling.couple.get_female_and_male()
            if mother_or_father_need_breeding_evaluation(mother, father, coupling) == True:
                form = FindCageForBroodAndMotherMoveAskBreedingSuccess()
            else:
                form = FindCageForBroodAndMotherMove()

        var_dict = {'form_move_brood_with_mother': form, 'move': True, 'whynotmovemessage': whynotmovemessage,\
                    'cage': cage, 'birds': birds, }
        return direct_to_template(request, 'birdlist/cage_overview.html', var_dict)



def move_family(request, cagename):
    '''
    '''
    from birdlist.forms.birdlist_formsets import FindCageForFamilyMove
    from birdlist.utils.bird import do_animal_transfer

    cage = get_object_or_404(Cage, name=cagename)
    birds = Bird.objects.filter(cage=cage).order_by('name')

    if request.method == 'POST':
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )

        form = FindCageForFamilyMove(request.POST)
        if 'movebutton' in request.POST:
            whynotmovemessage = ''
            if form.is_valid():
                coupling = Coupling.objects.get(cage__name=cagename, separation_date=None)
                            
                new_cage_id = request.POST['cage']
                new_cage = Cage.objects.get(pk = new_cage_id)
                
                if new_cage.occupancy() == 0:
                
                    # rename juveniles if necessary
                    rename_juveniles(birds.exclude(name__in = coupling.couple.get_female_and_male()), cagename, new_cage.name)
                    
                    # move all birds
                    for i in birds:
                        do_animal_transfer(i, new_cage_id, request.user)
                    
                    # move coupling
                    coupling.cage = new_cage
                    coupling.save()
                    return HttpResponseRedirect(new_cage.get_absolute_url(), )
                    
                else:
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append('Can not move family to non-empty cage.')

            var_dict = {'form_move_family': form, 'move': True, 
                    'whynotmovemessage': whynotmovemessage, 'cage': cage, 'birds': birds, }
            return direct_to_template(request, 'birdlist/cage_overview.html', var_dict)

    else:
        couplings = Coupling.objects.filter(cage=cage, separation_date=None)
        nbr_couples = couplings.count()

        whynotmovemessage = ''
        if nbr_couples == 0:
            whynotmovemessage = 'There is no couple in this cage.'

        form = FindCageForFamilyMove()
        var_dict = {'form_move_family': form, 'move': True, 'whynotmovemessage': whynotmovemessage,\
                    'cage': cage, 'birds': birds, }
        return direct_to_template(request, 'birdlist/cage_overview.html', var_dict) 


def separate_couple(request, cagename):
    '''
    '''
    from birdlist.forms.birdlist_formsets import FindCageForSeparatedCouple, FindCageForSeparatedCoupleAskBreedingSuccess

    cage = get_object_or_404(Cage, name=cagename)
    if cage.function == cage.FUNCTION_BREEDING:
        birds = Bird.objects.filter(cage=cage).order_by('date_of_birth')
    else:
        birds = Bird.objects.filter(cage=cage).order_by('name')

    if request.method == 'POST':
        
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )

        if 'separatebutton' in request.POST:
        
            # find out which Form to use.
            evaluate_breeding = False
            if request.POST.has_key('evaluate_breeding'):
                evaluate_breeding = request.POST['evaluate_breeding']

            # we need to check for the string "True" here, because POST contains
            # strings.
            if evaluate_breeding == 'True':
                evaluate_breeding = True
                form = FindCageForSeparatedCoupleAskBreedingSuccess(request.POST)
                breeder_status = request.POST['breeder_status']
            else:
                form = FindCageForSeparatedCouple(request.POST)
                breeder_status = None

            if form.is_valid():
                SeparationError = handle_couple_separation(form.cleaned_data['cage_male'],\
                        form.cleaned_data['cage_female'], cage, request.user, evaluate_breeding, breeder_status)
                if SeparationError:
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append(SeparationError)

                    var_dict = {'cage': cage, 'birds': birds, 'form_juvs': form, 
                                'separate':True, }
                    return direct_to_template(request,
                                'birdlist/cage_overview.html', var_dict)

                return HttpResponseRedirect(cage.get_absolute_url(), )

            var_dict = { 'cage': cage, 'birds': birds, 'form_separate': form, 
                        'separate': True, }
            return direct_to_template(request, 'birdlist/cage_overview.html',\
                var_dict)


    else:
        whynotseparatemessage = ''

        couplings = Coupling.objects.filter(cage=cage, separation_date=None)
        nbr_couples = couplings.count()
        form = FindCageForSeparatedCouple()
        
        if nbr_couples == 0:
            whynotseparatemessage = 'There is no couple in this cage.'
        elif nbr_couples == 1:
            coupling = couplings[0]
            mother, father = coupling.couple.get_female_and_male()
            birds_in_cage = birds.exclude(id__in = (father.id, mother.id))
            if birds_in_cage.__len__() > 0:
                whynotseparatemessage = "Please move juvenile birds out of this cage first."
            if mother_or_father_need_breeding_evaluation(mother, father, coupling) == True:
                form = FindCageForSeparatedCoupleAskBreedingSuccess()
                
        elif nbr_couples > 1:
            whynotseparatemessage = 'More than one couple seems to be in this cage. This is a problem. Talk to HOB.'

        var_dict = {'form_separate': form, 'separate': True, 'whynotseparatemessage': whynotseparatemessage,\
                    'cage': cage, 'birds': birds, }
        return direct_to_template(request, 'birdlist/cage_overview.html', var_dict) 

            
def go_to_cage(request):

    cage_id = ''
    cage_name = ''
    if request.POST.has_key('gotocage'):
        cage_id = request.POST['gotocage']
                    
    if request.POST.has_key('gotocage-textfield'):        
        cage_name = request.POST['gotocage-textfield']
 
    if cage_id or cage_name:
        # this is dirty, we should have a check at the end to make sure one condition
        # is satisfied
        if cage_id:
            cages = Cage.objects.filter(id=cage_id)
        else:
            cages = Cage.objects.filter(name=cage_name)
             
        if cages.__len__() == 1:
            cage = cages.get()
            return HttpResponseRedirect(reverse('cage_overview', args=(cage.name, )))

    return HttpResponseRedirect(reverse('index_cage', args=()))      


def edit_coupling_comment(request, cagename):
    cage = get_object_or_404(Cage, name=cagename)
    if cage.function == cage.FUNCTION_BREEDING:
        birds = Bird.objects.filter(cage=cage).order_by('date_of_birth')
    else:
        birds = Bird.objects.filter(cage=cage).order_by('name')

    if request.method == 'POST':
        form = EditCommentCouplingForm(request.POST)
        # in a POST we can only have one coupling
        coupling = Coupling.objects.filter(cage=cage, separation_date=None)[0]
        
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(cage.get_absolute_url(), )

        if 'savebutton' in request.POST:
            if form.is_valid():
                coupling.comment = form.cleaned_data['comment']
                coupling.save()
                return HttpResponseRedirect(cage.get_absolute_url(), )

            var_dict = { 'cage': cage, 'birds': birds, 'form_couplingcomment': form, 'change': True, }
            return direct_to_template(request, 'birdlist/cage_overview.html',\
                var_dict)


    else:
        couplings = Coupling.objects.filter(cage=cage, separation_date=None)
        nbr_couples = couplings.count()

        whynocomment = ''
        if nbr_couples == 0:
            whynocomment = 'There is no couple in this cage.'
            form = None
        elif nbr_couples == 1:
            coupling = couplings[0]
            form = EditCommentCouplingForm(instance=coupling)
        else:
            whynocomment = 'There is more than one couple in this cage. This should not happen. Please inform HOB.'
            form = None

        var_dict = {'form_couplingcomment': form, 'change': True, 'whynocomment': whynocomment,\
                    'cage': cage, 'birds': birds, }
        return direct_to_template(request, 'birdlist/cage_overview.html', var_dict)


