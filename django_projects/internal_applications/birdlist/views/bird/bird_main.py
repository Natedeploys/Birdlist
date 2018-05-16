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

from django.db.models import Q

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.forms.util import ErrorList

import datetime


from birdlist.forms.birdlist_formsets import FindBirdForm, BirdForm, SelectCageForm, FindBirdsForNewCouple, ReserveBirdForm, CheckoutAnimalFromColonyForm, SexAnimalForm
from birdlist.models import Bird, Cage, Activity, LabRoom, Activity_Type, Coupling
from birdlist.utils.bird import generate_qr_code, find_offspring, get_juveniles, get_adults, do_animal_transfer, find_birds_currently_breeding, rename_juveniles, do_cancel_reservation


def index(request):
    return direct_to_template(request, 'bird_index.html')


def list_all_birds(request):
    '''
    '''
    birds = Bird.objects.all().select_related().order_by('cage')
    
    return direct_to_template(request, 'birdlist/bird_list_ordered.html',\
            {'birds': birds})


def list_all_birds_alive(request, species=None, sex=None, cagetype=None):
    '''
    '''

    queryset = Bird.objects.filter(exit_date=None)


    warning = None
    header = ''


    if species == None or species == 'all':
        header = "all birds alive sorted by age"
        pass

    elif species == 'zf':
        queryset = queryset.filter(species=Bird.SPECIES_ZEBRAFINCH)
        header = "zebra finches alive sorted by age"

    elif species == 'bf':
        queryset = queryset.filter(species=Bird.SPECIES_BENGALESEFINCH)
        header = "bengalese finches alive sorted by age"

    else:
        warning = "your species filter is invalid - all shown"


    if cagetype == None or cagetype == 'all':
        pass

    elif cagetype == 'storage':
        #queryset = queryset.filter(Q(Q(cage__function=Cage.FUNCTION_LONGTERMSTORAGE)|Q(cage__function=Cage.FUNCTION_TEMPORARYSTORAGE)))
        queryset = queryset.filter(cage__function=Cage.FUNCTION_LONGTERMSTORAGE)
        header += ' in storage cages'

    elif cagetype == 'breeding':
        queryset = queryset.filter(cage__function=Cage.FUNCTION_BREEDING)
        header += ' in breeding cages'

    elif cagetype == 'breedingbreak':
        queryset = queryset.filter(cage__function=Cage.FUNCTION_BREEDINGBREAK)
        header += ' in breeding cages'

    else:
        warning = 'your cagetype choice is invalid - all shown'


    if sex == None or sex == 'all': 
        pass

    elif sex == 'm':
        queryset = queryset.filter(sex=Bird.SEX_MALE)
        header = 'male ' + header 

    elif sex == 'f':
        queryset = queryset.filter(sex=Bird.SEX_FEMALE)
        header = 'female ' + header 

    elif sex == 'u':
        queryset = queryset.filter(sex=Bird.SEX_UNKNOWN_JUVENILE)
        header = 'no sex juvenile ' + header 

    elif sex == 'v':
        queryset = queryset.filter(sex=Bird.SEX_UNKNOWN_NOT_VISIBLE)
        header = 'no sex ' + header 

    else:
        warning = 'your sex choice is invalid - all shown'


    #queryset = queryset.exclude(date_of_birth=None)
    queryset = queryset.select_related() 
    queryset = queryset.order_by('date_of_birth')

    if warning:
        header = warning

    view_type = 'agelist'

    extra_context = {'header': header, 'view_type': view_type}

    return object_list(request, queryset = queryset, extra_context = extra_context)


''' not used anymore
def find(request):
    #
    #
    form = FindBirdForm()
    if request.method == 'POST':
        bird_id = request.POST['bird']
        if bird_id:
            return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))

    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, })
'''

def bird_overview(request, bird_id):
    '''
    '''
    birds = Bird.objects.filter(id=bird_id)
    if birds.count() != 1:
        return render_to_response('birdlist/bird_notonebirdfound.html',\
                {'birds': birds}, context_instance=RequestContext(request))
    else:
        bird = birds[0]
        
        activities = Activity.objects.filter(bird=bird).order_by('start_date', 'id').reverse()
        openexperiments = activities.filter(activity_type__name='Experiment', end_date=None)
        a = generate_qr_code(bird)
        
        mydict = {'bird': bird,
                  'offspring': find_offspring(bird.id),
                  'activities': activities,
                  'openexperiments': openexperiments,
                  'img': a
                 }
        return render_to_response('birdlist/bird_overview.html', 
                            mydict, context_instance=RequestContext(request))

''' not needed anymore
def bird_print(request, bird_id):
    #
    #
    birds = Bird.objects.filter(id=bird_id)
    if birds.count() != 1:
        return render_to_response('birdlist/bird_notonebirdfound.html',\
                {'birds': birds}, context_instance=RequestContext(request))
    else:
        bird = birds[0]
        mydict = {'bird': bird,
                  'offspring': find_offspring(bird.id),
                  'activities': Activity.objects.filter(bird=bird).order_by('start_date').reverse(),
                 }
        return render_to_response('birdlist/print/print_bird.html',\
                mydict, context_instance=RequestContext(request))
'''
    
def show_juveniles(request):
    queryset = get_juveniles().select_related()
    header = 'all juvenile birds < 70 days'
    view_type = 'cage'
    extra_context = {'header': header, 'view_type': view_type}
    return object_list(request, queryset = queryset, extra_context = extra_context)    


def show_juveniles_by_age(request):
    queryset = get_juveniles().select_related().order_by('date_of_birth', 'cage')
    header = 'all juvenile birds < 70 days - sorted by age'
    view_type = 'cage'
    extra_context = {'header': header, 'show_link_juveniles_by_age_pdf': True, 'view_type': view_type}
    return object_list(request, queryset = queryset, extra_context = extra_context)    


def show_adults(request):
    queryset = get_adults().select_related()
    males, females = find_birds_currently_breeding()
    queryset = queryset.exclude(id__in = males)
    queryset = queryset.exclude(id__in = females)
    
    header = 'all adult birds > 90 days'
    view_type = 'cage'
    extra_context = {'header': header, 'view_type': view_type}
    return object_list(request, queryset = queryset, extra_context = extra_context)


''' remove or replace - don't forget to update url.py '''
def show_juveniles_breeding(request):
    queryset = get_juveniles()
    queryset = queryset.filter(cage__function = Cage.FUNCTION_BREEDING).order_by('cage')
    header = 'all birds < 70 days in breeding cage'
    view_type = 'cage'
    extra_context = {'header': header, 'view_type': view_type}
    return object_list(request, queryset = queryset, extra_context = extra_context)


''' not used anymore
from django.views.generic.create_update import create_object
def create(request):
    # basic view - needs all the POST routines, as in experiment_main.py, "new_bird"
    return create_object(request, form_class = BirdForm, 
        template_name = "birdlist/forms/form_basic.html",
        extra_context = {'add': True, 
        'change': False, })
'''

''' not used anymore
# first let the user search for a bird, then ask him for the new cage
def transfer(request):
    form = FindBirdForm()
    if request.method == 'POST':
        bird_id = request.POST['bird']
        if bird_id:
            return HttpResponseRedirect(reverse('transfer_bird_id', args=(bird_id, )))

    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Select bird', 'form_object_name': 'bird',  'title': 'transfer bird', })
'''

def transfer_bird_id(request, bird_id):
    form = SelectCageForm()
    bird = Bird.objects.get(pk = bird_id)
    
    # link to previous page (if given)
    prev = ''
    if request.GET.has_key('prev'):
        prev = request.GET['prev']
    if request.POST.has_key('prev'):
        prev = request.POST['prev']        

    if request.method == 'POST':
        form = SelectCageForm(request.POST)
        cage_id = request.POST['cage']
        
        if form.is_valid() and cage_id:
        
            cage_error = False
            cage = Cage.objects.get(pk = cage_id)
            cage_function = cage.function
            bird_cage_function = bird.cage.function
            
            # don't allow separation of breeding couples.
            if bird.is_breeding() == True:
                error_message = "This bird is part of a breeding couple. You have to separate the couple. Alternatively you can move the entire family."
                cage_error = True            

            # transfer to current cage makes no sense.            
            if bird.cage.id == int(cage_id):
                error_message = "This is the current cage of this bird. Please select different cage."
                cage_error = True

            # if moved to OutOfColony / dispoal bird must have an exit_date
            if cage_function == Cage.FUNCTION_DISPOSAL and bird.exit_date == None:
                error_message = "Please mark animal as dead before you move it to its final destination."
                cage_error = True

            # is the current cage a juvenile cage?            
            JUVENILE_IN_BREEDING_CAGE = False
            if (bird_cage_function == Cage.FUNCTION_BREEDING or \
                    bird_cage_function == Cage.FUNCTION_ISOLATIONDEVELOPMENTAL or 
                    bird_cage_function == Cage.FUNCTION_ISOLATIONRECORDINGS):
                JUVENILE_IN_BREEDING_CAGE = True
                
            # is the new cage a non juvenile cage?
            NEW_CAGE_IS_NOT_JUVENILE_CAGE = False
            if (cage_function == Cage.FUNCTION_LONGTERMSTORAGE or \
                    cage_function == Cage.FUNCTION_SOCIAL or \
                    cage_function == Cage.FUNCTION_BREEDINGBREAK):
                NEW_CAGE_IS_NOT_JUVENILE_CAGE = True
                
            # if bird is moved out of breeding or a developmental isolation cage bird must have a sex                
            if (JUVENILE_IN_BREEDING_CAGE and bird.sex == Bird.SEX_UNKNOWN_JUVENILE) and \
                    NEW_CAGE_IS_NOT_JUVENILE_CAGE:
                error_message = "Bird is moved out of juvenile cage but has no sex assigned. You must assign a sex first before you can move the bird."
                cage_error = True
            
            
            RENAME_JUVENILE = False
            if JUVENILE_IN_BREEDING_CAGE and bird.name[0] == bird.JUVENILE_PREFIX:
                if NEW_CAGE_IS_NOT_JUVENILE_CAGE:
                    error_message = "Bird is moved out of juvenile cage but has no proper name. You must ring this animal before you can move it into a new cage."
                    cage_error = True
                elif not NEW_CAGE_IS_NOT_JUVENILE_CAGE:
                    RENAME_JUVENILE = True
            
            
            cage_check, error_message_restriction = cage.check_restriction(bird.sex)
            if cage_check == False:
                error_message = "Can not transfer this animal into this cage, because the cage has a restriction that is not met: " + error_message_restriction
                cage_error = True

            if cage_error == True:
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append(error_message)
                return direct_to_template(request, 'birdlist/forms/form_search.html', {
                'form': form, 'select': 'Select cage', \
                'form_object_name': 'bird', 'title': 'transfer bird', \
                'bird': bird, 'prev': prev, })            


            # rename juvenile if necessary
            if RENAME_JUVENILE:
                rename_juveniles(Bird.objects.filter(pk = bird.id), bird.cage.name, cage.name)
                # need to grab this bird again. otherwise we will use the old data for the transfer
                # below - and will thus lose the renaming
                bird = Bird.objects.get(pk = bird_id)

            # everything is ok - move animal
            do_animal_transfer(bird, cage_id, request.user)
            if prev:
                return HttpResponseRedirect(prev)
            else:
                return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))

    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Select cage', 'form_object_name': 'bird', \
        'title': 'transfer bird', 'bird': bird, 'prev': prev, })


def sex_bird_id(request, bird_id):
    form = SexAnimalForm()
    bird = Bird.objects.get(pk = bird_id)
    
    # link to previous page (if given)
    prev = ''
    if request.GET.has_key('prev'):
        prev = request.GET['prev']
    if request.POST.has_key('prev'):
        prev = request.POST['prev']
        
    if request.method == 'POST':
            form = SexAnimalForm(request.POST)
            if form.is_valid():
                sex_field = form.cleaned_data['sex']
                if sex_field == 'none':
                    errors = form._errors.setdefault("__all__", ErrorList())
                    errors.append("Please select a sex.")
                else:
                    bird.sex = sex_field
                    bird.save()
                    if prev:
                        return HttpResponseRedirect(prev)
                    else:
                        return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))
        
    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Set sex', 'form_object_name': 'bird', \
        'title': 'sex animal', 'bird': bird, 'prev': prev, })


def reserve_bird_id(request, bird_id):

    form = ReserveBirdForm()
    bird = Bird.objects.get(pk = bird_id)
    
    if request.method == 'POST':
    
        form_data = request.POST.copy()
        form = ReserveBirdForm(form_data)
        
        if form.is_valid():

            if form.cleaned_data['reserve_until'] < datetime.date.today():
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append("You cannot make a reservation into the past.")
                return direct_to_template(request, 'birdlist/forms/form_search.html', {
                'form': form, 'select': 'Reserve bird until this date', \
                'form_object_name': 'bird', 'title': 'reserve bird', 'bird': bird, })

            reserve_until = form_data['reserve_until']
            reserve_by = request.user
            
            bird.reserved_until = reserve_until
            bird.reserved_by = reserve_by
            bird.save()
            
            # create reservation activity
            reservation_type = Activity_Type.objects.get(name='Reservation')
            reser_text = 'Reservation made until %s.' % (reserve_until)
            
            today = datetime.date.today()
            reservation = Activity(activity_type=reservation_type, \
                activity_content=reser_text, \
                bird=bird, originator=request.user, start_date=today, \
                severity_grade = Activity.SEVERITY_NONE, end_date=None)
                
            reservation.save()
            
            
            return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))

    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Reserve bird until this date', \
        'form_object_name': 'bird', 'title': 'reserve bird', 'bird': bird, })


def cancel_reserviation_bird_id(request, bird_id):
    bird = Bird.objects.get(pk = bird_id)
    # cancel reservation only if current user has reserved animal
    # this is an addtional check, because the button itself will not show up
    # but I don't want people to guess the URL to still unreserve the bird.
    if bird.reserved_by == request.user:
        do_cancel_reservation(bird)
        
    return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))


def checkout_bird(request, bird_id):
    
    form = CheckoutAnimalFromColonyForm()
    bird = Bird.objects.get(id = bird_id)
        
    if request.method == 'POST':
        form_data = request.POST.copy()
        form = CheckoutAnimalFromColonyForm(form_data)
    
        if form.is_valid():

            from birdlist.utils.bird import check_checkout_conditions, do_checkout_from_database
            error = check_checkout_conditions(bird_id, bird)
            if error:
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append(error)
            else:
                do_checkout_from_database(bird, form_data['exit_date'], form_data['cause_of_exit'], request.user)
                return HttpResponseRedirect(reverse('bird_overview', args=(bird_id, )))

    # request = Get, or form invalid, or errors
    return direct_to_template(request, 'birdlist/forms/form_search.html', {
        'form': form, 'select': 'Send bird to final destination', 
        'form_object_name': 'bird', 'title': 'checkout bird', 'bird': bird, })



def catch_bird(request):

    bird_id = ''
    bird_name = ''
    if request.POST.has_key('birdtocatch'):
        bird_id = request.POST['birdtocatch']
    
    if request.POST.has_key('birdtocatch-textfield'):        
        bird_name = request.POST['birdtocatch-textfield']

    if bird_id or bird_name:
        # this is dirty, we should have a check at the end to make sure one condition
        # is satisfied
        if bird_id:
            birds = Bird.objects.filter(id=bird_id)
        else:
            birds = Bird.objects.filter(name=bird_name)
                    
        if birds.__len__() == 1:
            bird = birds.get()
            return HttpResponseRedirect(reverse('bird_overview', args=(bird.id, )))
        else:
            return render_to_response('birdlist/bird_notonebirdfound.html',\
                {'birds': birds}, context_instance=RequestContext(request))
    else:
        return direct_to_template(request, 'bird_index.html')


''' not used anymore

def importfromzut4(request, birdname):

    birdName = birdname

    # check if bird already in database    
    queryset = Bird.objects.all();
    found = queryset.filter(name = birdName)
    if not found:
        print 'bird not in database!'
    else:
        print 'bird already in database'
        return render_to_response('birdlist/import_from_zut4.html', {'action_name': 'Bird already in database', 'bird': found[0]}, context_instance=RequestContext(request))

    from birdlist.utils.bird import do_import_from_zut4
    return do_import_from_zut4(birdName, request)
    
'''

## edit bird infos 
def bird_edit(request, bird_id):
    '''
    '''
    from birdlist.forms.bird_forms import BirdFormEdit

    # find bird, otherwise redirect to notonebirdfound template
    birds = Bird.objects.filter(id=bird_id)
    if birds.count() != 1:
        return direct_to_template(request,
                'birdlist/bird_notonebirdfound.html', {'birds': birds})
    else:
        bird = birds[0]
        
    # link to previous page (if given)
    prev = ''
    if request.GET.has_key('prev'):
        prev = request.GET['prev']
    if request.POST.has_key('prev'):
        prev = request.POST['prev']


    if request.method == 'POST':

        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('bird_overview', args=(bird.id, )))

        if 'savebutton' in request.POST:

            today = datetime.date.today()
            bird = Bird.objects.get(id=bird_id)

            # make copy of request.POST to make it mutable
            form_data = request.POST.copy()
            form = BirdFormEdit(form_data, instance=bird)

            #
            # ADD THINGS TO FORM

            # add time stamp if db exit / missing, remove it otherwise
            # only if cause of exit changed
            if form_data['cause_of_exit']!= str(bird.cause_of_exit):
                if form_data['cause_of_exit']=='':
                    form_data['missing_since'] = None
                    form_data['exit_date'] = None
                elif form_data['cause_of_exit']==str(Bird.EXIT_MISSING):
                    form_data['missing_since'] = today.isoformat()
                    form_data['exit_date'] = None
                else:
                    form_data['exit_date'] = today.isoformat()

            print form_data['cause_of_exit']
            
            # create bird transfer if cage changed
            if form_data['cage'] != str(bird.cage.id):
                from birdlist.utils.bird import do_animal_transfer
                # print form_data['cage']
                # print int(form_data['cage'])
                do_animal_transfer(bird, int(form_data['cage']), request.user)

            # add rename activity if bird was renamed/ringed
            if form_data['name'] != str(bird.name):
                rename_at = Activity_Type.objects.get(name='Renaming')
                rename_string = 'bird was renamed/ringed from %s to %s' % (str(bird.name), form_data['name'])
                rename_activity = Activity(bird=bird, activity_type=rename_at, \
                        activity_content=rename_string, originator=request.user, \
                        start_date=datetime.date.today(), \
                        end_date=datetime.date.today(), severity_grade = Activity.SEVERITY_NONE)
                rename_activity.save()
            
            if form.is_valid():
                form.save()
                if prev:
                    return HttpResponseRedirect(prev)
                else:
                    return HttpResponseRedirect(reverse('bird_overview', args=(bird.id, )))
                
                

            else:
                return direct_to_template(request,
                       'birdlist/forms/bird_edit.html',
                       {'form': form, 'bird': bird, 'change': True, 'prev': prev,})

    else:
        form = BirdFormEdit(instance=bird)

    return direct_to_template(request, 'birdlist/forms/bird_edit.html',
            {'form': form, 'bird': bird, 'change': True, 'prev': prev,})
            
            
def show_personal_reservations(request):
    username = request.user.username
    # it might make sense to only show reserved birds that are alive ...
    # queryset = Bird.objects.filter(reserved_by__username__exact = username, exit_date = None).order_by('cage')
    queryset = Bird.objects.filter(reserved_by__username__exact = username).order_by('cage').select_related()
    header = 'All birds reserved for ' + username
    view_type = 'cage'
    extra_context = {'header': header, 'view_type': view_type, }
    return object_list(request, queryset = queryset, extra_context = extra_context)
           
def show_common_reservations(request):
    # it might make sense to only show reserved birds that are alive ...
    # queryset = Bird.objects.filter(reserved_by__isnull=False, exit_date = None).order_by('cage')
    queryset = Bird.objects.filter(reserved_by__isnull=False).order_by('cage').select_related()
    header = 'All reserved birds'
    view_type = 'cage'
    extra_context = {'header': header, 'show_link_reservations_pdf': True, 'view_type': view_type, }
    return object_list(request, queryset = queryset, extra_context = extra_context)


from tagging.views import tagged_object_list
from tagging.utils import get_tag           
def show_bird_tags(request, tag=None):

    # show tag cloud
    if tag == None:
        mydict = {'coupling_choices': Bird.COUPLING_CHOICES, }
        return direct_to_template(request, 'birdlist/basic/tag_cloud.html', mydict)
        
    # show list of animals matching tag or coupling status.
    else:
    
        # check if user is looking up a tag or a coupling status.
        coupling_query = False
        coupling_value = None
        for i in Bird.COUPLING_CHOICES:
            if tag == i[1]:
                coupling_query = True
                coupling_value = i[0]
                break

        # sort by coupling status
        if coupling_query == True:
            queryset = Bird.objects.filter(coupling_status = coupling_value)
            extra_context = {'tag': tag, 'header_name': 'coupling status', }
            return object_list(request, queryset = queryset, paginate_by = 25,
                                    template_name='birdlist/basic/tags.html', 
                                    extra_context = extra_context)
        
        # sort by tag
        else:
            queryset = Bird.objects.all()
            extra_context = {'header_name': 'tag', }
            return tagged_object_list(request, queryset, tag, paginate_by = 25,
                extra_context = extra_context, 
                allow_empty=True, template_name='birdlist/basic/tags.html')

    
# url(r'^bird/(?P<bird_id>\d+)/test/
def test(request, bird_id):
    ''' dummy view used to benchmark different functions '''
    
    import time
    from birdlist.models import CoupleLookup
    bird = Bird.objects.get(id=bird_id)

    t0 = time.time()
    
    for i in range(1, 10000):
        if bird.sex == bird.SEX_MALE:
            clu = bird.father_set.all().values_list('couple', flat = True)
        else:
            clu = bird.mother_set.all().values_list('couple', flat = True)
        
        #couple_ids = CoupleLookup.objects.filter(Q(Q(father = bird.id) | Q(mother = bird.id))).values_list('couple', flat = True)
        
        
    #print time.time() - t0, "seconds"

    #
    #birds = Bird.objects.filter(id=bird_id)
    #mates = birds[0].get_mates_dict()
    
    return not_implemented(request, "externalview")


# url(r'^bird/(?P<bird_id>\d+)/show_family_tree/
def show_family_tree(request, bird_id):
    
    bird = Bird.objects.get(id=bird_id)
    mydict = {'bird': bird,
              'family': bird.build_family_tree(), }
    
    return direct_to_template(request, 'birdlist/bird_family_tree.html', mydict)



