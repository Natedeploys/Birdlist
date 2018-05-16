import datetime
from django.db.models import Q

from lablog.views.basic.lablog_main import not_implemented, server_error
from birdlist.models import Cage, Activity, Activity_Type, Bird, CoupleLookup, Coupling



def calc_date_bird(days):
    today = datetime.date.today()
    timedelta = datetime.timedelta(days = days)
    reference_date = today - timedelta
    return reference_date    


def calc_juvenile_date():
    return calc_date_bird(70)


def calc_adult_date():
    return calc_date_bird(90)


def get_juveniles():
    reference_date = calc_juvenile_date()
    queryset = Bird.objects.filter(date_of_birth__gte = reference_date, exit_date = None).order_by('cage')
    return queryset


def get_adults():
    reference_date = calc_adult_date()
    queryset = Bird.objects.filter(date_of_birth__lte = reference_date, exit_date = None).order_by('cage')
    return queryset


def do_animal_transfer(bird, new_cage_id, user, date = None):
    '''
    new_cage_id has to be an integer!!
    '''
    
    # if no date given, take today.
    if date == None:
        date = datetime.date.today()
         
    # log cage transfer
    new_cage = Cage.objects.get(pk = new_cage_id)
    attf = Activity_Type.objects.get(name='Cage Transfer')
    transfertext = 'bird was moved from %s to %s' % (bird.cage.name, new_cage.name)
    transfer = Activity(activity_type = attf, activity_content = transfertext, \
               bird = bird, originator = user, start_date = date, end_date = date, \
               severity_grade = Activity.SEVERITY_NONE)
               
    transfer.save()
    
    # save bird
    bird.cage = new_cage   
    bird.save()

    
def generate_qr_code(bird):
    # try / except here because we rely on an external service.
    try:
        from pygooglechart import QRChart
        # Create a 125x125 QR code chart
        chart = QRChart(125, 125)
        # Add the text
        string = 'BirdName: ' + bird.name + '\n Birthday: ' + bird.date_of_birth.__str__() + '\n URL: https://zongbird-db.lan.ini.uzh.ch' + bird.get_absolute_url()
        chart.add_data(string)
        # "Level H" error correction with a 0 pixel margin
        chart.set_ec('H', 0)
        # get url
        a = chart.get_url()
        return a
    except:
        return []
        
''' not used anymore        
def do_import_from_zut4(birdName, request):

    try:
        base_url = 'http://zut4/index.php?choice=1&cagename=&submit=Go!&field[]=0&field[]=1&xml&birdname='
        url_to_open = base_url + birdName
        from urllib2 import urlopen, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener, install_opener

        # create a password manager
        password_mgr = HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of ``None``.
        username = 'songbird'
        password = 'finch@ini'
        password_mgr.add_password(None, url_to_open, username, password)

        handler = HTTPBasicAuthHandler(password_mgr)

        # create "opener" (OpenerDirector instance)
        opener = build_opener(handler)

        # Install the opener.
        # Now all calls to urllib2.urlopen use our opener.
        install_opener(opener)

        a = urlopen(url_to_open).read()

        from xml.dom import minidom
        xmldoc = minidom.parseString(a)

        # get the field value
        birdname = xmldoc.getElementsByTagName('Birdname')[0].childNodes[0].nodeValue
        if xmldoc.getElementsByTagName('Species')[0].childNodes.length == 0:
            species = 'unknown'
        else:
            species = xmldoc.getElementsByTagName('Species')[0].childNodes[0].nodeValue
            
        if xmldoc.getElementsByTagName('Sex')[0].childNodes.length == 0:
            sex = 'u'
        else:
            sex = xmldoc.getElementsByTagName('Sex')[0].childNodes[0].nodeValue.lower()
            
            
        birthday = xmldoc.getElementsByTagName('Birthday')[0].childNodes[0].nodeValue
        uncertainty = xmldoc.getElementsByTagName('Uncertainty')[0].childNodes[0].nodeValue
        uncertainty = -1*int(uncertainty)
        
        
        cage = xmldoc.getElementsByTagName('Cage')[0].childNodes[0].nodeValue
        queryset = Cage.objects.all()
        found = queryset.filter(name = cage)
        if found.__len__() == 0:
            found = queryset.filter(name = 'Missing')
            
        cage = found[0]        
        
        if xmldoc.getElementsByTagName('Comment')[0].childNodes.length == 0:
            comment = ''
        else:
            comment = xmldoc.getElementsByTagName('Comment')[0].childNodes[0].nodeValue
            
        # father = xmldoc.getElementsByTagName('Father')[0].childNodes[0].nodeValue
        # mother = xmldoc.getElementsByTagName('Mother')[0].childNodes[0].nodeValue        
        # reserved = xmldoc.getElementsByTagName('Reserved')[0].childNodes[0].nodeValue

        if species == 'unknown':
            bird = Bird(name=birdname, sex=sex, date_of_birth=birthday, age_uncertainty=uncertainty, cage=cage, comment=comment)
        else:
            bird = Bird(name=birdname, species=species, sex=sex, date_of_birth=birthday, age_uncertainty=uncertainty, cage=cage, comment=comment)
            
        bird.save()

        return render_to_response('birdlist/import_from_zut4.html', {'action_name': 'Bird was added', 'bird': bird}, context_instance=RequestContext(request))   
        
    except:
        return server_error(request)
'''

def find_offspring(bird_id):
    '''
        returns offspring of bird, together with all information about the offspring
    '''
    bird = Bird.objects.get(id = bird_id)
    return bird.get_offspring().select_related()
        
        
def show_offspring(request, bird_id):
    bird = Bird.objects.get(pk = bird_id)
    queryset = Bird.objects.all()
    offspring = find_offspring(bird_id)
    extra_context = {'offspring': offspring, 'nbr_offspring': offspring.count()}

    return object_detail(request, queryset = queryset, 
            object_id = bird_id, extra_context = extra_context, 
            template_name='birdlist/bird_offspring.html')        
        

def find_birds_currently_breeding():

    couples_breeding = CoupleLookup.objects.filter(couple__in = Coupling.objects.filter(separation_date=None, type = Coupling.COUPLING_TYPE_BREEDING_COUPLE).values_list('couple', flat=True))            

    males_in_couples = couples_breeding.values_list('father', flat = True)
    females_in_couples = couples_breeding.values_list('mother', flat = True)
    return males_in_couples, females_in_couples
        
        
def find_birds_for_breeding(use_exact_method=False):

    from django.db.models import Q

    queryset_male = Bird.objects.filter(~Q(cage__function = Cage.FUNCTION_DISPOSAL) 
        & Q(sex = Bird.SEX_MALE, 
            cage__function__gt = Cage.FUNCTION_BREEDING, exit_date = None, missing_since = None))
            
    queryset_female = Bird.objects.filter(~Q(cage__function = Cage.FUNCTION_DISPOSAL) 
        & Q(sex = Bird.SEX_FEMALE, 
            cage__function__gt = Cage.FUNCTION_BREEDING, exit_date = None, missing_since = None))    

    if use_exact_method:
        # if a bird was breeding in the last 60 days, exclude him / her from the list
        reference_breeding_brake = calc_date_bird(60)
        
        # we only have to execute these queries if we really want to use the 'exact method'

        # all birds currently breeding or separated within the last 60 days
        birds_excluded = CoupleLookup.objects.filter(couple__in = 
            (Coupling.objects.filter(Q(separation_date = None) | 
            Q(separation_date__gte = reference_breeding_brake)).values_list('couple', flat=True)))
        
        # all males / females from previous lookup
        males_to_exclude = birds_excluded.values_list('father', flat = True)
        females_to_exclude = birds_excluded.values_list('mother', flat = True)
        # "correct" & exact query
        queryset_male = queryset_male.exclude(id__in = males_to_exclude)
        queryset_female = queryset_female.exclude(id__in = females_to_exclude)


    # bird should be at least 90 days old for breeding
    reference_min_breeding_age = calc_date_bird(90)
    
    queryset_male = queryset_male.exclude(date_of_birth__gte = reference_min_breeding_age).exclude(coupling_status = Bird.COUPLING_DO_NOT_COUPLE).order_by('-date_of_birth')
    queryset_female = queryset_female.exclude(date_of_birth__gte = reference_min_breeding_age).exclude(coupling_status = Bird.COUPLING_DO_NOT_COUPLE).order_by('-date_of_birth')

    # i guess it is reasonable to restrict the cages bird are suggested to be 
    # taken from to long term storage cages and breeding break cages
    queryset_male = queryset_male.filter(Q(Q(cage__function=Cage.FUNCTION_LONGTERMSTORAGE) | Q(cage__function=Cage.FUNCTION_BREEDINGBREAK))).select_related()
    queryset_female = queryset_female.filter(Q(Q(cage__function=Cage.FUNCTION_LONGTERMSTORAGE) | Q(cage__function=Cage.FUNCTION_BREEDINGBREAK))).select_related()
    
    return queryset_male, queryset_female 


def find_available_good_previous_couples(use_exact_method=False):
    '''
    '''
    import datetime
    today = datetime.date.today()


    # ~ 0.00886 seconds
    males, females = find_birds_for_breeding(use_exact_method = use_exact_method)


    # slow part starts here - get_mates_dict() is the bottleneck

    # since there are generally less females than males we go through the females
    # and see whether we find a successful male available

    couples = []
    female_list = []
    male_list = []
        
    # keep a separate dictionary for the male separation days - we can use it 
    # below for the couples
    male_sep = dict()
    # dictionary for male age
    male_age = dict()
    # dictionary for male father
    male_father = dict()
    # dictionary for male mother
    male_mother = dict()
    
    for male in males:
    
        male_dict_entire = male.get_mates_dict()
        separation = male_dict_entire['last_separation']
        separation = separation_to_days_since(separation, today)
        
        this_male_age = male.get_phd(return_empty = True)

        mother, father = male.get_mother_and_father()
        
        male_sep[male.id] = separation
        male_age[male.id] = this_male_age
        male_father[male.id] = ''
        male_mother[male.id] = ''
        if father:
            male_father[male.id] = father.id
        if mother:
            male_mother[male.id] = mother.id
        
        mates = male_dict_entire['mates']
        mate_string = get_mates_string_from_dict(mates)
        
        male_list.append({ 'bird': male, 'last_separation': separation, \
                            'mates': mate_string, 'father': father, \
                            'mother': mother, 'age': this_male_age, })


    for fm in females:

        fm_dict = fm.get_mates_dict()
        last_separation = fm_dict['last_separation']
        last_separation = separation_to_days_since(last_separation, today)
        
        female_age = fm.get_phd(return_empty = True)
        
        mates = fm_dict['mates']
        mate_string = get_mates_string_from_dict(mates)
        
        mother, father = fm.get_mother_and_father()        
        
        female_list.append({ 'bird': fm, 'last_separation': last_separation, \
                            'mates': mate_string, 'father': father, \
                            'mother': mother, 'age': female_age, })


        for mate in mates:
            male = mate['bird']
            if not (male in males):
                continue

            # don't suggest animals that are brother & sister                
            if father and mother:                
                if male_father[male.id] == father.id or male_mother[male.id] == mother.id:
                    continue
                
            # set the criterion that a couple must have had more than 2 
            # generations offspring on average per coupling 
            # to be preferably reused for breeding
            # on average we had 1.7 broods per coupling
            # so we select better than average couples
            if mate['AvgNoBroods'] >= 2:
                couple_dict= {
                        'male': male, 
                        'female': fm,
                        'male_cage': male.cage.name,
                        'female_cage': fm.cage.name, 
                        'AvgNoBroods': mate['AvgNoBroods'],
                        'AvgNoJuvs': mate['AvgNoJuvs'],
                        'female_last_separation': last_separation,
                        'male_last_separation': male_sep[male.id],
                        'female_age': female_age,
                        'male_age': male_age[male.id],
                        }
                couples.append(couple_dict)

    return couples, male_list, female_list, list(males.values_list('id', flat = True)), list(females.values_list('id', flat = True))
    
    
def separation_to_days_since(separation, today):
    if separation:
        separation = today - separation
        separation = separation.days
    else:
        separation = ''        
        
    return separation
    
    
def get_mates_string_from_dict(mydict):
    mate_string = ''
    for i in mydict:
        mate_string = mate_string + i['bird'].name + '(' + str(int(i['AvgNoBroods'])) + ' - ' + str(i['last_separation']) + '), '
        
    if mate_string:
        mate_string = mate_string[:-2]        
        
    return mate_string


def rename_juveniles(birds, oldcagename, newcagename):
    ''' renames all animals of a given querylist birds '''
    for i in birds:
        # enforce renaming of juvenile birds only.
        if i.name[0] == i.JUVENILE_PREFIX:
            i.name = i.name.replace(oldcagename, newcagename)
            i.save()


def check_checkout_conditions(bird_id, bird):

    # DONE - if no reason -> don't do it
    # DONE - if experiment open -> don't do it
    # DONE - bird already dead
    # DONE - if animal breeding -> don't do it
    # DONE - if reserved -> don't do it

    activities = Activity.objects.filter(bird__id = bird_id).order_by('start_date', 'id')
    openexperiments = activities.filter(activity_type__name = 'Experiment', end_date = None).__len__()
    
    if openexperiments > 0: # open experiment
        error = "Please close any open experiments first."
    elif bird.exit_date: # bird dead                
        error = "This bird is already at its final destination."
    elif bird.is_breeding():
        error = "This bird is part of a breeding couple. Please separate the couple first."
    elif bird.reserved_by:
        error = "This bird is reserved - please cancel the reservation first."
    else:
        error = None
    
    return error


def do_checkout_from_database(bird, exit_date, cause_of_exit, user):

    # DONE - if juvenile -> set unique type to none
    # DONE - move animal to cemetery            

    cage = Cage.objects.filter(id = bird.cage_id)
    in_cage = cage.__len__()

    is_juvenile = 0

    # is juvenile - check 1
    if in_cage:
        cage_name_length = bird.cage.name.__len__()
        if bird.name[0:1+cage_name_length] == bird.JUVENILE_PREFIX + bird.cage.name:
            is_juvenile = 1
    # is juvenile - check 2
    if bird.sex == Bird.SEX_UNKNOWN_JUVENILE:
        is_juvenile = 1
    
    # set name_unique to None - let's hope this works.     
    if is_juvenile == 1:
        bird.name_unique = None
        
    bird.exit_date = exit_date
    bird.cause_of_exit = int(cause_of_exit)
    cage = Cage.objects.get(function = Cage.FUNCTION_DISPOSAL)
    do_animal_transfer(bird, cage.id, user, bird.exit_date)


def do_cancel_reservation(bird, cancel_string = None):
    bird.reserved_until = None
    bird.reserved_by = None
    bird.save()
    
    # find reservation activity and update its content
    today = datetime.date.today()
    
    default_string = "\n Reservation was revoked on %s." % (today)
    if cancel_string:
        string_to_use = cancel_string
    else:
        string_to_use = default_string
    
    a = Activity.objects.get(bird = bird, activity_type__name = "Reservation", end_date = None)
    a.activity_content = a.activity_content + string_to_use
    a.end_date = today
    a.save()


