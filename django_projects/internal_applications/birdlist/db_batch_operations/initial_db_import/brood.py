# having created couplings in an earlier step we now figure out into which coupling (session) a birds birthday fits
# we then create or find the brood and assign it to the coupling

from birdlist.models import Couple, Coupling, Brood, CoupleLookup, Bird, Cage
from coupling import find_bird_obj
from coupling import create_coupling

from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER,\
        BIRDLIST_FILE, COUPLING_FILE, BIRTHDAY_TOLERANCE

from birdlist.dbconversion.birds import IGNORED_BIRDS

import time


# overall procedure
# ---------------------------------------------------------------------
def generate_broods(debug=0, birthday_tolerance=BIRTHDAY_TOLERANCE):
    '''
    '''
    delete_old_entries(debug=debug)
    # I am using a different approach than Andreas
    #lookup = create_lookup_couple_juvenile();
    #create_new_brood_entries(lookup);
    stats_birthday_after_coupling, problem_broods = assign_parents_couple(debug=debug, birthday_tolerance=birthday_tolerance)

    print 'all done'

    return stats_birthday_after_coupling, problem_broods


def delete_old_entries(debug=0):
    '''
    '''
    # kill all data
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('TRUNCATE TABLE `birdlist_brood`')
    cursor.close()
    connection.close()

    print 'deleted old entries'


def assign_parents_couple(debug=0, birthday_tolerance=BIRTHDAY_TOLERANCE):
    '''
    go through all the birds in the birdlist import file

        -> find couple that are parents
            if None:
                save bird_id in list

        -> find coupling session
            ** diff(start_coupling, birthday)
            ** coupling_duration

        -> find brood via birthday_tolerance
            if None:
                -> create brood

        -> assign brood to bird
            -> increase uncertainty to max if necessary

    check birds with no parents

    do stats
    '''

    # logging
    from birdlist.dbconversion.logger import logger
    lognotes = 'B R O O D - G E N E R A T I O N   L O G'
    log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation.log', log_notes=lognotes)
    lognotes = 'B R O O D - G E N E R A T I O N   E R R O R - L O G'
    ERROR_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation_ERROR.log', log_notes=lognotes)
    lognotes = 'B R O O D - G E N E R A T I O N   M I S S I N G   P A R E N T S - L O G'
    MISSING_PARENTS_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation_MISSING_PARENTS.log', log_notes=lognotes)
    lognotes = 'B R O O D - B O U G H T   B I R D'
    BOUGHT_BIRD_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation_BOUGHT_BIRD.log', log_notes=lognotes)

    # statistic containers
    stats_birthday_after_coupling = []
    stats_intrabrood_birthday_diff = []

    # read and process database transfer csv-file
    import csv
    file = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE)
    fileReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')

    # an old breeding cage as default breeding cage if breeding cage cannot be assigned
    default_cage = Cage.objects.get(id = 50)

    # now loop through all rows/birds of source file
    for birdy in fileReader:
        
        ## GET BIRD INFO READY FOR PROCESSING

        # ignore the first row and any tweak birds and birds in ignored_birds
        if birdy[0].__contains__('Birdname') or birdy[0].upper().__contains__('TWEAK') or birdy[0] in IGNORED_BIRDS:
            print 'did not import and thus do not handle in this context bird: ' + birdy[0]
            continue

        # ordered list of csv row attributes
        import_list = ['name', 'species', 'sex', 'birthday', 'uncertainty', 'cage',\
                'father', 'mother', 'exit date', 'cause of exit', 'comment', 'reserved', ]

        # fill in bird-container
        bird = {}
        for i, item in enumerate(import_list):
            bird[item] = str(birdy[i])

        # ----------------------------
        if debug:
            import_message = '\n\n' + bird['name'] + '\n-----------------------------------\n'
            for item in bird:
                import_message = import_message + item + ': ' + bird[item] + '\n'
            import_message = import_message + '-----------------------------------\n\n' \
            
            print import_message
        # ----------------------------

        # convert birthday to string of form YYYY-MM-DD
        if bird['birthday']:
            bird['birthday'] = convert_date(bird['birthday'])
   
        # get the corresponding django bird instance
        try:
            django_bird = Bird.objects.get(name=bird['name'])
        except:
            # write to log and jump out of loop
            error_log_message = 'could not find bird in new database (name: %s - mum: %s - dad: %s)' % (bird['name'], bird['mother'], bird['father'])
            ERROR_log.write_string_to_log(error_log_message)
            continue
        
        # store the id for logging purposes
        bird['new id'] = django_bird.id


        ## HANDLE COUPLE INFO FOR SPECIFIC BIRD
        # we basically have to care for three different cases:

        # 1 - if father and mother exist try to find the corresponding django couple
        if bird['father'] and bird['mother']:

            # try to find corresponding django couple - function returns None if no couple can't be found
            couple_id = find_couple_id(bird['father'], bird['mother'])
            if couple_id == None:
                # log and jump out of loop
                # TODO : maybe we should still write db-inconsistent parental information into comment field
                error_log_message = 'could not find PARENT COUPLE for this bird (name: %s - id: %s - mum: %s - dad: %s - birthday: %s)' % (bird['name'], bird['new id'], bird['mother'], bird['father'], bird['birthday'])
                ERROR_log.write_string_to_log(error_log_message)
                continue
            # else: continue further down with finding coupling sessions and broods ..

        # 2 - if both father and mother do not exist bird is probably bought -> see whether we can assign a specific purchase event by looking at the comment
        elif not (bird['father'] and bird['mother']):
            # we display birdname and comment field to see whether we can figure out something about the origin of the bird
            print '\n\nNO PARENT BIRDS FOR:'
            print bird['name']
            print '-------------------------------------'
            print bird['comment'] + '\n'
            bought = raw_input('do you find origin information in the comment field (y/n)? ')
            if bought == 'y':
                date_of_purchase = raw_input('can you figure out when the bird was obtained (YYYY-MM-DD / n)? ')
                supplier = raw_input('can you figure out from whom we got the bird (supplier name)? ')
                # TODO : now find same event 'broods'
                purchase_brood = Brood.objects.filter(origin=ORIGIN_EXTERNAL)
            else:
                # in that case we do not know anything about the parents -> write this into comment field
                django_bird.comment = django_bird.comment + '\nno information about this birds origin could be found in the db at import'
                django_bird.save()
            continue

        # 3 - the only case remaining is that either father or mother is missing but not both -> write info into birds comment field
        else:
            MISSING_PARENTS_message = 'MUM OR DAD IS MISSING at import (name:$%s$- id:$%s$- mum:$%s$- dad:$%s$- comment:$%s$)' % (bird['name'], bird['new id'], bird['mother'], bird['father'], bird['comment'])
            MISSING_PARENTS_log.write_string_to_log(MISSING_PARENTS_message)
            # write missing parents 
            django_bird.comment = str(django_bird.comment) + ' - ' + MISSING_PARENTS_message
            django_bird.save()
            continue
        
        ## FIND COUPLING SESSION
        # if we have a birthday and a couple id find the coupling session that contains the birthday
        if bird['birthday']:
            try:
                coupling = find_coupling(couple_id, bird['birthday'])
                stats_birthday_after_coupling.append(date_diff_days(coupling.coupling_date.isoformat(), bird['birthday']))
            except:
                # log and jump out of loop
                error_log_message = 'COUPLING SESSION not found: (name: %s - id: %s - mum: %s - dad: %s - birthday: %s)' % (bird['name'], bird['new id'], bird['mother'], bird['father'], bird['birthday'])
                ERROR_log.write_string_to_log(error_log_message)
                continue
        else:
            # bird has no birthday -> log & jump out
            error_log_message = 'this bird has no birthday, the rest would be fine?!?: (name: %s - id: %s - mum: %s - dad: %s)' % (bird['name'], bird['new id'], bird['mother'], bird['father'])
            ERROR_log.write_string_to_log(error_log_message)
            continue

        ## FIND OR CREATE BROOD
        # find brood within birthday_tolerance
        brood = find_brood_within_tolerance(coupling.id, bird['birthday'], birthday_tolerance, debug=debug)
        # assign brood
        if brood:
            # add birthday to comment field for later corrections
            brood.comment = brood.comment + ' %s;' % bird['birthday'] 
            # check if uncertainty is equal, correct otherwise to the larger value
            if bird['uncertainty']:
                try:
                    uncertainty = -int(bird['uncertainty'])
                except:
                    uncertainty = -8
                if brood.age_uncertainty > uncertainty and uncertainty != -8:
                    brood.age_uncertainty = uncertainty
            
        # or create new one
        else:
            # TODO: assign origins 'correctly'
            # if bird has birthday
            # -> check comment field
            #    if 'bought' in comment field 
            # !! already filtered out on line 140
            # if bird has not birthday -> external
            # --> find buy occasion if possible
            if bird['uncertainty']:
                uncertainty = -int(bird['uncertainty'])
            else:
                uncertainty = -8
            brood = Brood(origin=Brood.ORIGIN_BREEDING, date_of_birth=bird['birthday'], \
                    age_uncertainty=uncertainty, coupling=coupling, comment=bird['birthday']+';')

        brood.save()
        django_bird.brood = brood
        django_bird.save()
    
    # all data is entered from the csv-file -> we can close it
    file.close()

    # now we have to go through all the brood entries and correct the birthdays where there were different ones entered
    problem_broods = clean_brood_birthdays()

    return stats_birthday_after_coupling, problem_broods






# HELPER FUNCTIONS
# ----------------------------------------------------

def clean_brood_birthdays():
    '''
    '''
    allbroods = Brood.objects.all()

    problem_broods = []

    import scipy
    counter = 0
    for brood in allbroods:
        
        birthdays_epochtime_list = isodatestringlist_to_epochtimelist(string_splitstrip_to_list(brood.comment, ';'))
        bdet_array = scipy.array(birthdays_epochtime_list)
        if bdet_array.min() == bdet_array.max():
            continue
        else:
            max_diff = (bdet_array.max() - bdet_array.min()) / (60*60*24)
            problem_broods.append([brood.id, brood.comment, max_diff])
            counter = counter + 1

    print 'corrected %s birthdays in total' % counter

    return problem_broods


def string_splitstrip_to_list(string, delimeter):
    '''
    '''
    list = []
    for item in string.rsplit(delimeter):
        list.append(item.split())

    return list


def isodatestringlist_to_epochtimelist(list):
    '''
    '''
    epochtimelist = []

    for date in list:
        if date:
            epochtimelist.append(time.mktime(time.strptime(str(date[0]), "%Y-%m-%d")) + 12*60*60)

    return epochtimelist


def find_brood_within_tolerance(coupling_id, birthday, birthday_tolerance, debug=0):
    '''
    '''
    broods_of_coupling = Brood.objects.filter(coupling=coupling_id)
    
    # ----------------------------
    if debug:
        print broods_of_coupling
    # ----------------------------

    considerable_broods = []
    
    for brood in broods_of_coupling:
        # find if birthday is within birthday_tolerance
        brood_birthday = str(brood.date_of_birth)
        lower_bound = add_days_to_isodate(brood_birthday, -birthday_tolerance) 
        upper_bound = add_days_to_isodate(brood_birthday, birthday_tolerance) 
        if date_is_within_dates(birthday, lower_bound, upper_bound):
            considerable_broods.append(brood)

    if considerable_broods.__len__()==1:
        return considerable_broods[0]
    elif considerable_broods.__len__()>1:
        print 'more than one brood within BIRTHDAY TOLERANCE'
        return
    else:
        return


def find_couple_id(father_name, mother_name):
    '''
    '''
    try:
        couple_lookup = CoupleLookup.objects.get(father__name__exact = father_name, mother__name__exact = mother_name)
        couple = couple_lookup.couple
        return couple

    except:
        print 'no couple_lookup found for father: %s - mother: %s' % (father_name, mother_name)
        # return None if no couple could be found
        return 



def find_coupling(couple_id, birthday, debug=0):
    '''
    '''
    try:
        possible_couplings = Coupling.objects.filter(couple=couple_id)
    except:
        print 'NO COUPLING SESSION FOUND AT ALL!?!'
        return

    considerable_couplings = []
    today = time.strftime('%Y-%m-%d', time.gmtime())
   
    # loop throug all couplings of this couple
    for coupling in possible_couplings:
        
        # safety check: coupling date should not be empty
        if coupling.coupling_date != None:
            coupling_date = coupling.coupling_date.isoformat()

            # if separation date is empty -> make it today
            if coupling.separation_date != None:
                separation_date = coupling.separation_date.isoformat()
            else:
                # separation day is today if separation day is empty
                separation_date = today 
        else:
            print 'ATTENZIONE !! !! !! coupling date == None'
            return

        # now see whether the dates are 'in a row'
        try:
            within = date_is_within_dates(birthday, coupling_date, separation_date)
        except:
            print
            print 'ATTENZIONE !! !! !! could not calculate WITHIN !!!!!!!!!'
            print coupling_date
            print birthday
            print separation_date
            return

        # if separation date is empty check if birthdate is not before coupling date, i.e. between coupling date and today
        if coupling.separation_date == None:
            if date_is_within_dates(birthday, '2000-01-01', coupling_date):
                within = False

        if within: 
            considerable_couplings.append(coupling)
    
    if considerable_couplings.__len__()>1:
        print 'ATTENZIONE !! !! !! more than one considerable coupling for this bird - WTF?!'

    else:
        return considerable_couplings[0]


def date_diff_days(date1_string, date2_string):
    '''
    enter date strings with format YYYY-MM-DD
    '''
    date1 = time.mktime(time.strptime(date1_string, "%Y-%m-%d"))
    date2 = time.mktime(time.strptime(date2_string, "%Y-%m-%d"))

    return (date2-date1)/(60*60*24)
    

def date_is_within_dates(date_string, start_string, end_string):
    '''
    enter date strings in isoformat YYYY-MM-DD as strings
    and check whether date is within start and end
    return True or False
    '''

    date = time.mktime(time.strptime(date_string, "%Y-%m-%d"))
    start = time.mktime(time.strptime(start_string, "%Y-%m-%d"))
    
    if end_string != None:
        end = time.mktime(time.strptime(end_string, "%Y-%m-%d"))
    else:
        return False
   
    if end < start:
        raise NameError('you entered an end_date that is smaller than the start_date!')
    
    if date<=end and date>=start:
        return True
    else:
        return False


def add_days_to_isodate(date_string, plusdays):
    '''
    add a plusdays to date which has to be given in iso format (YYYY-MM-DD) as a string
    return a string 
    '''
    # add an hour such that we do not have any 'day border effects'
    date = time.mktime(time.strptime(date_string, "%Y-%m-%d")) + 1*60*60
    plussecs = plusdays*60*60*24
    return time.strftime("%Y-%m-%d", time.gmtime(date+plussecs))
    




## ----------------------------------------------------------------------------------------------
## KOTO


def create_lookup_couple_juvenile():
    '''
    creates a lookup table
    '''

    lookup = {}
    import csv
    file = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE)

    testReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')

    nbr_birds_skipped = 0
    outbreeders = 0
    mumordadmissing = 0
    nocouplingentry = 0

    # an old cage
    default_cage = Cage.objects.get(id = 50)

    for row in testReader:

        index = 0
        # pk = row[0]
        name = row[index]
        # ignore the first row and any tweak birds
        if name.__contains__('Birdname') or name.upper().__contains__('TWEAK') or name == '':
            print 'skipping bird: ' + name
            nbr_birds_skipped = nbr_birds_skipped + 1
            continue

        index = index + 1
        species = row[index]

        index = index + 1
        sex = row[index]
        if sex == 'M':
            sex = 'm'
        elif sex == 'F':
            sex = 'f'
        elif sex == '':
            sex = 'u'

        index = index + 1
        birthday = row[index]    
        if birthday == '':
            birthday = '2007-12-24'
        else:
            birthday = convert_date(birthday)

        index = index + 1
        uncertainty = row[index]

        if uncertainty and uncertainty.isdigit():
            uncertainty = int(uncertainty)
            uncertainty = uncertainty.__neg__()
        else:
            uncertainty = 0

        index = index + 1
        cage = row[index]
        cage = find_cage_id(cage)

        ## father & mother

        index = index + 1
        father = row[index]
        if father == '':
            father = None
        else:
            father = find_bird_obj(father)

        index = index + 1
        mother = row[index]
        if mother == '':
            mother = None
        else:
            mother = find_bird_obj(mother)

        # if no mum and no dad: mark as outbreeder - not really exact, because 
        # of the way we breed BF
        if mother == None and father == None:
            print 'no mum and no dad found for: ' + name
            this_bird = find_bird_obj(name)
            this_bird.outbreeder = True
            this_bird.save()
            outbreeders = outbreeders + 1
            continue

        # either mum or dad are missing
        if mother == None or father == None:
            print 'either mum or dad are missing for: ' + name
            mumordadmissing = mumordadmissing + 1
            continue


        # debugging statements to check if the mapping is correct
        if mother.name == 'g19r2' and father.name == 'o12r8':
            print name
            bird = find_bird_obj(name)
            print bird.pk.__str__()

        # both mum and dad exist.
        # is couple in our database?
        try:
            #couple_lookup = CoupleLookup.objects.get(father = father, mother = mother)
            # let's find the coupling entry - we will get multiple results for 
            # birds that have coupled multiple times
            # coupling = Coupling.objects.get(couple = couple_lookup.couple)
            # this does not work :( 64 vs 240 entries ...
            # maybe be I already filter out the case where more than one event 
            # matches?
            couple = find_couple(bird['father'], bird['mother'])
            
            if bird['birthday']:
                coupling = find_coupling(couple, bird['birthday'])
                stats_birthday_after_coupling.append(date_diff_days(coupling.start_date, bird['birthday']))
            couple = find_couple(father, mother)

            # debugging statements to check if the mapping is correct
            if mother.name == 'g19r2' and father.name == 'o12r8':
                print couple.id.__str__()

        # no couple found, but both mum and dad exist
        # let's create a new couple & coupling entry
        except:
            string = 'no couple entry found for bird ' + name + ' will create missing entry, male; female ' + father.name + '; ' + mother.name
            print string
            nocouplingentry = nocouplingentry + 1
            create_fake_coupling_entry(name, mother, father, default_cage)
            couple = find_couple(father, mother)

        # now a couple exists, but how about a coupling entry? it will only be 
        # generated in the 'except' case


        # lookup list. associate each juvenile with the correct couple id        
        bird = find_bird_obj(name)
        bird_id = bird.pk.__int__()
        couple_id = couple.pk.__int__()
        if lookup.has_key(couple_id):
            #print 'adding entry to: ' + couple_id.__str__()
            lookup[couple_id].append(bird_id)
        else:
            #print 'creating couple id: ' + couple_id.__str__()
            lookup[couple_id] = [bird_id]

    file.close();
    
    # show statistics
    print 'a total of: ' + nbr_birds_skipped.__str__() + ' birds were skipped'
    print 'a total of: ' + nocouplingentry.__str__() + ' birds could not be assigned to a couple - but we know their mum and dad'
    print 'a total of: ' + outbreeders.__str__() + ' birds have been marked as outbreeders'
    print 'a total of: ' + mumordadmissing.__str__() + ' birds are missing either mum or dad'
    return lookup



def find_couple(father, mother):
    couple_lookup = CoupleLookup.objects.get(father = father, mother = mother)
    couple = couple_lookup.couple
    return couple


def find_couplings(father, mother, coupling_date = None):
    couple = find_couple(father, mother)
    if coupling_date:
        couplings = Coupling.objects.filter(couple = couple, coupling_date = coupling_date)
    else:
        couplings = Coupling.objects.filter(couple = couple)

    return couplings


def create_fake_coupling_entry(name, mother, father, default_cage):

    this_bird = find_bird_obj(name)
    coupling_date = this_bird.birthday
    separation_date = this_bird.birthday
    comment = ''
    cage = default_cage
    create_coupling(father, mother, cage, coupling_date, separation_date, comment)


def find_nbr_generations(comment_field):

    comments = comment_field
    # find the highest index, where ';' occours.
    generation_start = comments.rfind(';')
    generation = comments[generation_start+1:]
    if generation == ' ':
        nbr_gens = 0
    else:
        nbr_gens = int(generation[1])

    return nbr_gens


def find_family_for_couple(couple_id, offspring_ids):

    # test cases:
    # brood.find_family_for_couple(1,  a[1])
    # brood.find_family_for_couple(249,  a[249])

    total_generations = 0
    # how many days can pass so we consider birds to be the same generation?
    same_brood_range = 14

    # there might be not enough coupling entries. You will need to create them 
    # by hand. This is normal in cases where a) a couple already existed but b)
    # there was no coupling entry for a second coupling event

    # in addition we need to create a brood entry for each generation

    # we should always have a unique couple entry
    a = Couple.objects.get(id = couple_id)
    print 'Couple ID: ' + a.__str__()

    # there might be multiple coupling events for this couple
    c = Coupling.objects.filter(couple__id = couple_id)
    print 'Coupling IDs: ' + c.__str__()

    for i in c:    
        print 'Coupling date ' + i.coupling_date.__str__()
        print 'Separation date: ' + i.separation_date.__str__()
        generations = find_nbr_generations(i.comment)
        total_generations = total_generations + generations
        print 'generations in DB: ' + generations.__str__()


    b = CoupleLookup.objects.get(couple = a)
    print 'Father: ' + b.father.name
    print 'Mother: ' + b.mother.name

    offspring = Bird.objects.filter(id__in = offspring_ids).order_by('birthday')
    for i in offspring:
        print 'offspring: ' + i.name

    print '       '

    #
    print total_generations.__str__() + ' generations are entered into the database'
    birthdays = offspring.values_list('birthday').distinct()
    nbr_birthdays = birthdays.__len__()
    print  nbr_birthdays.__str__() + ' unique birthdays found: '
    for i in birthdays:
        print '         ' + i.__str__()

    if total_generations == nbr_birthdays:
        print 'the number of generations matches the number of birthdays'
    else:
        print 'please fix the number of generations'

def create_new_brood_entries(lookup):
    ## find couple information

    for bla in lookup:

        print bla
        ## find brothers and sisters of this bird

        #siblings = Bird.objects.filter(birthday__lte = coupling.separation_date, birthday__gte = coupling.coupling_date)
        print siblings

        print 'created new entries'



def convert_date(string):
    import time
    b = time.strptime(string, '%d.%m.%Y')
    string = time.strftime("%Y-%m-%d", b)
    return string


def find_cage_id(cage_to_find):

    from birdlist.models import Cage
    cage = None
    if cage_to_find:
        cage = Cage.objects.filter(name__exact = cage_to_find)
        if cage:
            cage = cage.get()
        else:
            cage = Cage.objects.filter(function = Cage.FUNCTION_MISSING).get()
    else:
        cage = Cage.objects.filter(function = Cage.FUNCTION_DISPOSAL).get()

    
    return cage

