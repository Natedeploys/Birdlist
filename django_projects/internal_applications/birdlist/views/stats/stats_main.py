import time

from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.db.models import Q

from birdlist.models import Activity, Activity_Type, Bird, Cage, Coupling, Animal_Experiment_Licence

from birdlist.forms.birdlist_formsets import FindBirdForm
from birdlist.forms.activity_forms import ActivityUserlist, ActivityLicenceList
from birdlist.utils.stats import get_newborns_per_week, get_couples_per_week, get_cage_occupancy_per_week, year_weeknumber_to_gregorian_calendar, find_timestamp_mismatch_new_activities, find_timestamp_mismatch_old_activities
from lablog.utils.experiment import query_latest


def index(request):
    return render_to_response('birdlist/stats_index.html', 
                                    context_instance=RequestContext(request))

def nbr_couples_and_new_borns_per_week(request):
    
    newborns = get_newborns_per_week()
    couples = get_couples_per_week()
    zero = int(0)

    # add zero value to list of couples, so if there was no offspring that value
    # we don't miss this element    
    counter = couples
    for i in counter:
        key = i
        value = counter[key]
        counter[key] = (value, zero)
        
    for i in newborns:
        this_week = i
        this_value = newborns[i]
        if counter.get(this_week):
            counter[this_week] = (counter[this_week][0], this_value)
        else:
            counter[this_week] = (zero, this_value)
    
    counter = sorted(counter.items(), reverse = True)
    counter2 = year_weeknumber_to_gregorian_calendar(counter)
    
    return render_to_response('birdlist/stats_nbr_birds_per_week.html', 
                {'counter': counter2, }, context_instance=RequestContext(request))


def nbr_animals_in_cage_per_week(request):

    '''
    This function used to take ~ 4.1 seconds, with 
    'get_cage_occupancy_per_week' only running for ~ 4.0 seconds.
    However, I fixed 'get_cage_occupancy_per_week' and now this page shouldn't
    take longer than one second!
    
    '''

    tStart = time.time()
    
    # force recomputing if parameter is present
    recompute = False
    if request.GET.has_key('recompute'):
        recompute = True

    # show user selected cage (if given)
    default_cage = 'KM'
    if request.GET.has_key('cage'):
        this_cage = request.GET['cage']
    else:
        this_cage = default_cage
        
    # use previously calculated results if available
    if request.session.has_key('animals_in_cage_per_week') and recompute == False:
        cage_usage = request.session['animals_in_cage_per_week']
    else:
        cage_usage = get_cage_occupancy_per_week()
        request.session['animals_in_cage_per_week'] = cage_usage

    # make sure cage name is in list (people might modify the URL)    
    if not cage_usage.has_key(this_cage):
        this_cage = default_cage

    # grab selected cage        
    this_cage_usage = cage_usage[this_cage]

    # create dict for selected cage
    a = dict()
    for i in this_cage_usage:
        a[i] = this_cage_usage[i]
    
    # sort current cage dict
    counter = sorted(a.items(), reverse = True)
    counter2 = year_weeknumber_to_gregorian_calendar(counter)
    
    # sort cage names so user can switch cages
    cage_names = sorted(cage_usage.keys())
    
    # measure how much time function call did take.
    t_in = str(round(time.time() - tStart, 4))
    
    return direct_to_template(request, 'birdlist/stats_nbr_animals_in_cage_per_week.html',
        {'counter': counter2, 'cage_name': this_cage, 'cage_names': cage_names, 'run_time': t_in})


def show_my_experiments(request):

    birdlist_query = Activity.objects.filter(activity_type = Activity_Type.objects.get(name='Experiment'), originator__username__exact = request.user.username).order_by('-start_date').select_related()
    
    vdict = {
        'experiments_in_animal_list': birdlist_query, }
    
    return direct_to_template(request, 'birdlist/stats_my_experiments.html', vdict)


def show_experiments_by_bird(request):
    '''
    creates a container with birds and their experiments
    ordered such that birds with an open experiments appear on top
    the rest should be sorted by the end_date of the last experiment
    '''

    experiments = Activity.objects.filter(activity_type__name='Experiment').order_by('-start_date')
    experiments = experiments.select_related()
    

    # this nested loop is not very elegant
    # could not come up with a better solution right now
    birdlist = []
    for experiment in experiments:
        appended = False
        for bird in birdlist:
            if experiment.bird == bird['bird']:
                bird['experiments'].append(experiment)
                appended = True
        if not appended:
            birdlist.append({'bird': experiment.bird, 'experiments': [ experiment, ]})

    vdict = { 'birdlist': birdlist, }
    
    return direct_to_template(request, 'birdlist/stats_experiments_by_bird.html', vdict)


def show_experiments_by_user(request):
    '''
    experiments by user is very similar to experiments by bird only that 
    only birds are shown that had an experment for a given user
    '''

    if request.method == 'POST':
        new_data = request.POST.copy()

        user_id = new_data['user']
        user = User.objects.get(id = user_id)      
        experiments = Activity.objects.filter(originator=user, activity_type__name='Experiment').order_by('-start_date')
        experiments = experiments.select_related()

        # this nested loop is not very elegant
        # could not come up with a better solution right now
        birdlist = []
        for experiment in experiments:
            appended = False
            for bird in birdlist:
                if experiment.bird == bird['bird']:
                    bird['experiments'].append(experiment)
                    appended = True
            if not appended:
                birdlist.append({'bird': experiment.bird, 'experiments': [ experiment, ]})
      
        pi = user.get_full_name() 

        vdict = {'birdlist': birdlist, 'pi': pi, 'content': 'Experiments', }
        return direct_to_template(request, 'birdlist/stats_experiments_by_bird.html', vdict)
    else:
        form = ActivityUserlist()
        vdict = {'form': form, 'search': True, 'do_not_show_cancel': True, 'content': 'Experiments', }
        return direct_to_template(request, 'birdlist/stats_activities_by_user.html', vdict)


def show_my_experiments(request):

    birdlist_query = Activity.objects.filter(activity_type = Activity_Type.objects.get(name='Experiment'), originator__username__exact = request.user.username).order_by('-start_date').select_related()
    
    vdict = {
        'experiments_in_animal_list': birdlist_query, }
    
    return direct_to_template(request, 'birdlist/stats_my_experiments.html', vdict)


def show_activities_by_user(request, user_id = 1):

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data.has_key('user'):
            user_id = new_data['user']

        activities = Activity.objects.filter(originator = user_id).order_by('-start_date').select_related()
        user = User.objects.get(id = user_id)      
        username = user.get_full_name()  
      
        vdict = {'activities': activities, 'user_looked_up': username, 'content': 'Activities', }
        return direct_to_template(request, 'birdlist/stats_activities_by_user.html', vdict)
    else:
        form = ActivityUserlist()
        vdict = {'form': form, 'search': True, 'do_not_show_cancel': True, 'content': 'Activities', }
        return direct_to_template(request, 'birdlist/stats_activities_by_user.html', vdict)


def show_experiments_by_licence(request, year = None):

    if request.method == 'POST':
        new_data = request.POST.copy()
        if new_data.has_key('licence'):
            licence_id = int(new_data['licence'])
            licence = Animal_Experiment_Licence.objects.get(id=licence_id)

        activities = Activity.objects.filter(activity_type__name='Experiment', animal_experiment_licence=licence).order_by('-start_date')
        if year:
            activities = activities.filter(Q(Q(start_date__year=year) | Q(end_date__year=year)))
      
        activities = activities.select_related()
        vdict = {'activities': activities, 'licence': licence}
        return direct_to_template(request, 'birdlist/stats_experiments_by_licence.html', vdict)
    else:
        form = ActivityLicenceList()
        vdict = {'form': form, 'search': True, 'do_not_show_cancel': True, }
        return direct_to_template(request, 'birdlist/stats_experiments_by_licence.html', vdict)


def show_experiments_without_licence(request, year = None):

    without_lic_exps = Activity.objects.filter(activity_type__name='Experiment', animal_experiment_licence=None).order_by('-start_date')
    if year:
        without_lic_exps = without_lic_exps.filter(Q(Q(start_date__year=year) | Q(end_date__year=year)))
    
    var_dict = { 'without_lic_exps': without_lic_exps, }

    return direct_to_template(request, 'birdlist/stats_experiments_without_licence.html', var_dict)


def show_activities_last_days(request, how_many_days = 2):
    import datetime
    
    filter_by_user = False
    if request.GET and request.GET.has_key('user'):
        username = request.GET['user']
        if len(User.objects.filter(username__in = [username,])):
            filter_by_user = True
        
    how_many_days = int(how_many_days)
    timedelta = datetime.timedelta(days = how_many_days)
    reference_date = datetime.datetime.today() - timedelta
    
    activities = Activity.objects.filter(Q(start_date__gt = reference_date) | Q(end_date__gt = reference_date)).order_by('-id').select_related()
    # don't filter the user list because we want to show all users that had activities
    # during the specified period.
    users = User.objects.filter(id__in = activities.values_list('originator', flat=True)).order_by('username')
    
    # filter list if filtering was requested
    if filter_by_user == True:
        activities = activities.filter(originator__username__in = [username, ])

    vdict = {'activities': activities, 'content': 'Activities', 
            'how_many_hours': how_many_days * 24, 'days_to_link': range(100), 
            'users': users, }
    return direct_to_template(request, 'birdlist/stats_activities_last_days.html', vdict)


# /stats/show_activities_timestamp_mismatch/
def show_activities_timestamp_mismatch(request):
    '''
        List of activities (created after June 23rd 2011 @ 17:50) with timestamp 
        mismatch.
    
    '''
    activities = find_timestamp_mismatch_new_activities()
    zipped_old = find_timestamp_mismatch_old_activities()
    
    
    vdict = {'activities': activities, 'activities_old': zipped_old, }
    return direct_to_template(request, 'birdlist/show_activities_timestamp_mismatch.html', vdict)


def show_experiments_open(request):
    '''
        all currently open experiments
    '''

    birdlist_query = Activity.objects.filter(activity_type = Activity_Type.objects.get(name='Experiment'), end_date = None).order_by('-start_date').select_related()
    vdict = { 'exps': birdlist_query, }
    return direct_to_template(request, 'birdlist/stats_experiments_open.html', vdict)


def all_animals_with_wrong_coupling_status(request):
    from birdlist.utils.bird import find_offspring
    
    birdlist_query = Bird.objects.filter(coupling_status = Bird.COUPLING_NEVER_USED, exit_date = None).order_by('-date_of_birth').select_related()
    remove_id = []
    for i in birdlist_query:
        if find_offspring(i.id).__len__() == 0:
            remove_id.append(i.id)
    # keep only animals that have offspring
    birdlist_query = birdlist_query.exclude(id__in = remove_id)
    
    vdict = { 'animals': birdlist_query, }
    return direct_to_template(request, 'birdlist/stats_animals_with_wrong_coupling_status.html', vdict)


def quick_hist_kotowicz(values, bin_size = 10, CUTOFF = 1000):
    '''
    histogram deals only with values > 0
    bins are (]
    '''
    
    from collections import defaultdict

    # counter for number of items beyond CUTOFF
    nbr_cutoff = 0

    # raw histogram
    d = defaultdict(int)
    
    # bin all values into bins of size '1' first
    for x in values:
        if x > CUTOFF:
            nbr_cutoff += 1
        else:
            d[x] += 1

    # calculate the true bins
    bin_edges = range(0, CUTOFF + 1, bin_size)
    # number of bins is one less than number of edges
    nbr_bins = bin_edges.__len__()-1
    
    # pre-allocate histogram with zeros
    binned_data = defaultdict(int)
    zero = int(0)
    for x in range(0, nbr_bins):
        binned_data[x] = zero

    # do the binning
    for x in d.iteritems():
        # skip values of 0
        if x[0] == 0:
            continue
        # have to subtract 1 from bin number
        # such that we look at intervals like (min, max]
        abs_bin_nbr = x[0]-1
        nbr_items_this_bin = x[1]
        mod_value = abs_bin_nbr.__divmod__(bin_size)
        bin_number = mod_value[0]
        binned_data[bin_number] += nbr_items_this_bin

    values_histogram = binned_data.values()
    mean_value = (sum(values) / values.__len__())
    
    return values_histogram, nbr_cutoff, mean_value


def colony_overview_stats(request):

    from birdlist.stats import colonystats as cs
   
    CUTOFF = 1000
    bin_size = 10
   
    # distribution of males and females
    all_ages_storage, no_a_nbd_storage, no_a_storage = cs.age_distribution(sex='all')
    distr_a_storage, no_a_b1000dph, mean_age_all = quick_hist_kotowicz(all_ages_storage, bin_size, CUTOFF)
    a_distr_chart = generate_distribution_plot(distr_a_storage)

    # distribution of males only
    male_ages_storage, no_m_nbd_storage, no_m_storage = cs.age_distribution(sex='m', cage_restriction='storage')
    distr_m_storage, no_m_b1000dph, mean_age_males = quick_hist_kotowicz(male_ages_storage, bin_size, CUTOFF)
    m_distr_chart = generate_distribution_plot(distr_m_storage)


    # distribution of females only
    female_ages_storage, no_f_nbd_storage, no_f_storage = cs.age_distribution(sex='f', cage_restriction='storage')
    distr_f_storage, no_f_b1000dph, mean_age_females = quick_hist_kotowicz(female_ages_storage, bin_size, CUTOFF)
    f_distr_chart = generate_distribution_plot(distr_f_storage)

    vdict = {

            'distr_a_storage': distr_a_storage,
            'no_a_b1000dph': no_a_b1000dph,
            'no_a_storage': no_a_storage,
            'mean_age_all': mean_age_all,
            'distr_a_chart': a_distr_chart, 

            'distr_m_storage': distr_m_storage,
            'no_m_b1000dph': no_m_b1000dph,
            'no_m_storage': no_m_storage,
            'mean_age_males': mean_age_males,
            'distr_m_chart': m_distr_chart, 
            
            'distr_f_storage': distr_f_storage,
            'no_f_b1000dph': no_f_b1000dph,
            'no_f_storage': no_f_storage,
            'mean_age_females': mean_age_females,
            'distr_f_chart': f_distr_chart,

            }

    return direct_to_template(request, 'birdlist/stats_colony_overview.html', vdict)



def generate_distribution_plot(histogram_data, y_max=20, x_max=1000):

    from GChartWrapper import VerticalBarStack
    
    G = VerticalBarStack( histogram_data, encoding='text')
    # set the color
    #G.color('4d89f9')
    # set bar thickness, between bar space, between group space
    G.bar(5,2,2)
    # set plot size
    G.size(800,200)
    # specify type of axis we want
    G.axes.type('xy')
    # scaling : !!?! scales the data only - has nothing to do with the range
    G.scale(0,y_max)
    # axes index, min, max, interval
    G.axes.range(0,0,x_max,50)
    G.axes.range(1,0,y_max,5)
    # show a grid
    G.grid(2,5,1,2)

    return G


