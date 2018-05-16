import datetime
import time
from birdlist.models import Activity, Bird, CoupleLookup, Coupling
from django.db.models import Q

UNKNOWN_BIRTHDAY = datetime.datetime(2007, 01, 01)


def iso_year_start(iso_year):
    '''
        The gregorian calendar date of the first day of the given ISO year
    '''
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    
    return fourth_jan - delta 


def iso_to_gregorian(iso_year, iso_week, iso_day):
    '''
        Gregorian calendar date for the given ISO year, week and day
    '''
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


def year_weeknumber_to_gregorian_calendar(counter):
    '''
        converts my custom YYYY - WW (year - week number) format back into
        the gregorian calendar
    '''

    counter2 = dict()
    for i in counter:
        date = i[0]
        value = i[1]
        new_key = str(iso_to_gregorian(int(date[0:4]), int(date[7:9]), 1))
        counter2[new_key] = value
    
    counter2 = sorted(counter2.items(), reverse = True)

    return counter2


def get_newborns_per_week():
    '''
    
        creates a dictionary of number of new borns per week 
        
    '''

    birds = Bird.objects.all().exclude(date_of_birth = None).order_by("-date_of_birth")
    counter = dict()
    for i in birds:
        iso_calendar = i.date_of_birth.isocalendar()
        this_year = str(iso_calendar[0])
        this_week = prepad_week_with_zero(iso_calendar[1])
            
        this_date = this_year + " - " + this_week
        
        if counter.get(this_date):
            counter[this_date] = counter[this_date] + 1
        else:
            counter[this_date] = 1
    
    return counter


def get_couples_per_week():
    '''
    
        creates a dictionary of number couples per week
        
    '''


    couplings = Coupling.objects.all().order_by('-coupling_date')
    
    today = datetime.datetime.today().isocalendar()
    this_year = today[0]
    this_week = today[1]
    
    counter = dict()
    
    for j in couplings:
        start_date = j.coupling_date.isocalendar()
        end_date = j.separation_date
        
        # if there is an end date, use it
        if end_date:
            end_date = j.separation_date.isocalendar()
            this_year_end = end_date[0]
            this_week_end = end_date[1]
            
        # no end date - use today.
        else:
            this_year_end = this_year
            this_week_end = this_week            
            
        # start            
        this_year_start = start_date[0]
        this_week_start = start_date[1]


        dates = create_week_numbers_from_range(this_year_start, this_year_end, this_week_start, this_week_end)

        # append to dict
        for i in dates:
            if counter.get(i):
                counter[i] = counter[i] + 1
            else:
                counter[i] = 1
    
    return counter


def get_cage_occupancy_per_week():
    ''' 
    
    calculates the maxium number of animals per cage of a given week
    
    '''

    #tStart = time.time()
    #tStart0 = time.time()
    
    today = datetime.datetime.today().isocalendar()
    
    from collections import defaultdict
    d = defaultdict(defaultdict)
    
    # old lookup - this lookup takes ~ 3.0 seconds, depending on the depth of select_related
    # a = Activity.objects.filter(activity_type__name = "Cage Transfer").order_by("bird", "start_date").select_related(depth = 2)
    # new lookup - only takes ~ 0.15 seconds, because we only return values
    a = Activity.objects.filter(activity_type__name = "Cage Transfer").order_by("bird", "start_date").select_related(depth = 2).values("bird__id", "bird__date_of_birth", "bird__cage__name", "end_date", "activity_content")
    nbr_entries = a.__len__()
    
    
    #t_in = time.time() - tStart
    #print "Activity lookup:" + str(t_in)
    
    prev_bird = ''
    start_date = ''
    counter = 0
    
    
    # loop takes ~ 0.58 seconds, if the activity lookup above returns all data 
    # and returns objects.
    # loop takes ~ 0.55 seconds, if the activity lookup above returns all data 
    # and returns values.
    #tStart1 = time.time()
    for i in a:
        counter = counter + 1
        this_bird = i['bird__id']
        
        if this_bird != prev_bird:
            prev_bird = this_bird
            start_date = i['bird__date_of_birth']
            # some birds have no birthday, we'll just ignore the first cage
            # because we don't know when the bird got introduced into the colony
            if not start_date:
                this_transfer_date = i['end_date']
                # print "skipping, bird: %s, birthday: none, transfer day: %s" %(i.bird, this_transfer_date)
                continue
        else:
            start_date = this_transfer_date
            
        this_content = i['activity_content']
        this_transfer_date = i['end_date']
            
        # extract cage name
        if this_content.startswith("old db transfer: moved out of cage"):
            cage_name = this_content.partition("old db transfer: moved out of cage ")[2]
            # cage_name = this_content.lstrip("old db transfer: moved out of cage")
        else:
            cage_name = this_content.partition("bird was moved from ")[2]
            cage_name = cage_name[:cage_name.find('to')-1]
            # this is wrong, because new transfer messages indicate both old & new cage.
            # cage_name = cage_name[cage_name.find('to')+3:]

        
        # people entered birthday incorrectly
        if this_transfer_date < start_date:
            # print "skipping cage transfer for %s, cage = %s" % (i.bird, cage_name)
            continue
        
        # don't distinguish between upper and lower case names
        cage_name = cage_name.upper()

        # convert dates to isocalendar
        start_date_iso = start_date.isocalendar()
        this_transfer_date_iso = this_transfer_date.isocalendar()
        
        # if this is the last transfer, then we need to log the current cage too
        DO_CURRENT_CAGE = False

        # the bird will change with the next activity
        if counter < nbr_entries and this_bird != a[counter]['bird__id']:
            DO_CURRENT_CAGE = True
        
        # log everything
        d = log_cage_occupancy(start_date_iso, this_transfer_date_iso, d, cage_name)
        
        # last activity for this bird - do additional transfer for current cage
        if DO_CURRENT_CAGE == True:
        
            start_date_iso = this_transfer_date_iso
            this_transfer_date_iso = today
            cage_name = i['bird__cage__name'].upper()
            
            d = log_cage_occupancy(start_date_iso, this_transfer_date_iso, d, cage_name)


    #t_in = time.time() - tStart1
    #print "loop a:" + str(t_in)
    #tStart = time.time()
    
    # take care of all animals that have no cage transfer and report their current
    # cage. If an animal has no birthday, we use a fake birthday UNKNOWN_BIRTHDAY
    b = Bird.objects.all().exclude(id__in = a.values_list('bird', flat = True)).select_related()
    
    #t_in = time.time() - tStart
    #print "Bird lookup:" + str(t_in)
    
    # this loop takes ~ 0.1 seconds
    for i in b:
        start_date = i.date_of_birth
        if not start_date:
            start_date = UNKNOWN_BIRTHDAY
        
        start_date_iso = start_date.isocalendar()
        this_transfer_date_iso = today
        cage_name = i.cage.name.upper()
        d = log_cage_occupancy(start_date_iso, this_transfer_date_iso, d, cage_name)

    #t_in = time.time() - tStart0
    #print "get_cage_occupancy_per_week:" + str(t_in)
    return d


def log_cage_occupancy(start_date_iso, this_transfer_date_iso, d, cage_name, bird_name = None):

    this_year_start = start_date_iso[0]
    this_year_end = this_transfer_date_iso[0]
    this_week_start = start_date_iso[1]
    this_week_end = this_transfer_date_iso[1]
    
    # create the year - week entries for this transfer
    dates = create_week_numbers_from_range(this_year_start, this_year_end, this_week_start, this_week_end)
    
    for j in dates:
        if d.has_key(cage_name) and d[cage_name].has_key(j):
            d[cage_name][j] = d[cage_name][j] + 1
        else:
            d[cage_name][j] = 1
            
    return d


def prepad_week_with_zero(week):
    week = str(week)
    if week.__len__() == 1:
        week = '0' + week
        
    return week


def create_week_numbers_from_range(this_year_start, this_year_end, this_week_start, this_week_end):
    ''' 
        This code assumes that every year has 53 weeks - which is not true.
        But I guess it doesn't really matter.
    '''

    # list of weeks in cage
    dates = []

    counter = 0
    while this_year_start != (this_year_end + 1):
    
        this_year_start_str = str(this_year_start)
        
        if counter == 0:
            start_week = this_week_start
        else:
            start_week = 1
        
        if this_year_start == this_year_end:
            end_week = this_week_end + 1
        else:
            end_week = 54
        
        for i in range(start_week, end_week):
            week = prepad_week_with_zero(i)
            this_date = this_year_start_str + " - " + week
            dates.append(this_date)

        counter += 1
        this_year_start += 1

    return dates


def find_timestamp_mismatch_new_activities():
    
    # exclude all activities created before June 23rd 2011, which have a fake 
    # timestamp.
    a = Activity.objects.all().exclude(timestamp_created = datetime.datetime(1991, 8, 25, 22, 57)).values_list('id', 'timestamp_created', 'start_date', 'end_date', 'timestamp_modified')
    
    # exclude back-dated stuff by 'hob' and "OutOfColony" moves
    a = a.exclude(Q(originator__username = "hob") | Q(activity_content__contains = "OutOfColony"))
    
    # create list of activities, where the day of timestamp_created != start_date
    # or timestamp_modified != end_date
    suspicious = list()
    for i in a:
        timestamp_created = datetime.datetime.date(i[1])
        timestamp_modified = datetime.datetime.date(i[4])
        start_date = i[2]
        end_date = i[3]
        
        start_date_mismatch = False
        mod_date_mismatch = False
        if not (timestamp_created == start_date):
            start_date_mismatch = True
        
        # end_date is 'None' if not set
        if end_date:
            if not (timestamp_modified == end_date):
                mod_date_mismatch = True

        if start_date_mismatch or mod_date_mismatch:
                suspicious.append(i[0])
    
    activities = Activity.objects.filter(id__in = suspicious).order_by('-id')
    return activities


def find_timestamp_mismatch_old_activities():
    # all old activities
    ANIMAL_DATABASE_KICKOFFDATE = datetime.date(2011, 1, 14)
    a = Activity.objects.all().filter(timestamp_created = datetime.datetime(1991, 8, 25, 22, 57)).exclude(start_date__lte = ANIMAL_DATABASE_KICKOFFDATE).values_list('id', 'start_date').order_by('id')
    
    # exclude back-dated stuff by 'hob' and "OutOfColony" moves
    a = a.exclude(Q(originator__username = "hob") | Q(activity_content__contains = "OutOfColony"))
    
    suspicious = list()
    possible_date = list()
    old_date = a[0][1]
    for i in a:
        new_date = i[1]
        if new_date < old_date:
            suspicious.append(i[0])
            possible_date.append(old_date)
        else:
            old_date = new_date
    
    activities_old = Activity.objects.filter(id__in = suspicious)
    
    # zip old activities together with possible_dates
    zipped_old = []
    count = 0
    for i in activities_old:
        this_date = possible_date[count]
        zipped_old.append((i, this_date))
        count = count + 1
        
    zipped_old = sorted(zipped_old, key=lambda entry: entry[0].id, reverse=True)
    return zipped_old



