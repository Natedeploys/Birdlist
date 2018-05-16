'''
set of functions aggregating colony statistics
'''
import datetime
from django.db.models import Q

from birdlist.models import Bird, Cage, Activity

def age_distribution(days_ago=0, sex='all', cage_restriction=None, species='zf'):
    '''
    returns a list of ages of birds alive days_ago of the given sex
    as well as the number of birds alive without date of birth
    
    to plot histogram use numpy and pylab:
    In [86]: agear = np.array(age_distribution)
    In [87]: pylab.hist(agear, np.arange(0,1500, 10))
    '''
    age_distribution = [] 
    birds_alive_with_no_birthday = 0

    date_of_reference = datetime.date.today() - datetime.timedelta(days_ago)

    # get birds that have an exit_date bigger than date_of_reference or no exit_date
    birds_alive = Bird.objects.filter(Q(Q(exit_date__gte=date_of_reference) | Q(exit_date=None)))
    # exclude birds that were born after date_of_reference
    birds_alive = birds_alive.exclude(date_of_birth__gte=date_of_reference)
    # select species
    birds_alive = birds_alive.filter(species=species)
    # exclude missing birds
    birds_alive = birds_alive.filter(missing_since=None)

    if sex == 'all':
        # do not filter if birds of all sexes should be included
        pass
    elif sex in (Bird.SEX_MALE, Bird.SEX_FEMALE, Bird.SEX_UNKNOWN_JUVENILE, Bird.SEX_UNKNOWN_NOT_VISIBLE):
        birds_alive = birds_alive.filter(sex=sex)
    else:
        raise ValueError('You did not provide a valid sex!')

    if cage_restriction == 'storage':
        birds_alive = birds_alive.filter(cage__function=Cage.FUNCTION_LONGTERMSTORAGE)

    for bird in birds_alive:

        if bird.date_of_birth == None:
            birds_alive_with_no_birthday += 1

        else:
            age = date_of_reference - bird.date_of_birth
            age_distribution.append(age.days)

    no_birds = age_distribution.__len__() + birds_alive_with_no_birthday

    return age_distribution, birds_alive_with_no_birthday, no_birds


def days_to_have_offspring_distribution():
    '''
    the days between broods or since coupling

    not fully tested
    '''
    from birdlist.models import Coupling

    days = []

    for coupling in Coupling.objects.all():
        broods = coupling.brood_set.all()

        # sort broods in order to be sure the first is the earliest
        brood_list = list(broods)
        brood_list.sort(key=lambda brood: brood.get_broods_birthday())

        for i, brood in enumerate(brood_list):
            # if its the first brood we have to look for the diff to the coupling date
            if i == 0: 
                diff = brood.get_broods_birthday() - coupling.coupling_date
                days.append(diff.days)

            else:
                previous_brood = brood_list[i-1]
                diff = brood.get_broods_birthday() - previous_brood.get_broods_birthday()
                days.append(diff.days)

    return days


def nbr_of_newborns_per_week():
    '''
    count the number of newborns between sundays starting from the week of the 
    first in colony newborn
    '''

    first_bd = Bird.objects.exclude(date_of_birth=None).exclude(brood=None).order_by('date_of_birth')[0].date_of_birth

    new_sunday = first_bd + datetime.timedelta(7-first_bd.isoweekday())
    old_sunday = new_sunday - datetime.timedelta(7)

    no_newbs_per_week = []
    sundays = []

    while new_sunday < datetime.date.today():
        
        # get the number of newborns in the current week
        no_newbs_in_week = Bird.objects.filter(date_of_birth__gt=old_sunday, date_of_birth__lte=new_sunday).count()
        no_newbs_per_week.append(no_newbs_in_week)

        sundays.append(new_sunday.isoformat())
        
        # update the week
        old_sunday = new_sunday
        new_sunday = new_sunday + datetime.timedelta(7)

    return no_newbs_per_week, sundays


def nbr_birds_per_week():
    '''
    !!! ATTENZIONE !!!
    function does not produce reliable results yet

    '''

    # start with collecting data in the week of the first newborn in our own colony
    first_bd = Bird.objects.exclude(date_of_birth=None).exclude(brood=None).order_by('date_of_birth')[0].date_of_birth

    new_sunday = first_bd + datetime.timedelta(7-first_bd.isoweekday())
    old_sunday = new_sunday - datetime.timedelta(7)

    no_birds_per_week = []
    sundays = []

    while new_sunday < datetime.date.today():
        
        # since not all birds have a birthday we cannot use the birthday
        # to assess when a bird 'entered the database'
        # we use the activity instead, this is not totally exact but a good estimate

        no_birds_with_act_before_date =\
                Activity.objects.filter(end_date__lte=new_sunday).values_list('bird__name').distinct().count()

        # birds that died before week
        birds_dead = Bird.objects.filter(exit_date__lte=old_sunday).count()

        # birds that had activities before minus the ones that died before
        no_birds_per_week.append(no_birds_with_act_before_date - birds_dead)

        # update the week
        old_sunday = new_sunday
        new_sunday = new_sunday + datetime.timedelta(7)

    return no_birds_per_week
