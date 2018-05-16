from django.db.models import Q
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from birdlist.models import Activity, Bird, Cage, Coupling
from birdlist.forms.birdlist_formsets import FindBirdForm

import datetime

def birdlistlogin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index_birdlist', ))
    else:
        return login(request, template_name = 'birdlist/basic/login.html' )


def index(request):
    ''' View for entrance page of lablog.
    '''
    # redirect user to personal start page if logged in
    if request.user.is_authenticated():

        open_experiments = Activity.objects.filter(activity_type__name='Experiment', originator__id=request.user.id, end_date=None).select_related()
        recent_activities = Activity.objects.filter(originator__id=request.user.id).order_by('start_date', 'id').select_related().reverse()[:10]

        _dict = {'open_experiments': open_experiments,
                 'recent_activities': recent_activities, }

        return direct_to_template(request, 'index.html', _dict)

    # otherwise send them to the login page      
    else:
        return HttpResponseRedirect(reverse('birdlistlogin'), )
        
# /birdlist/search/        
def search_database(request):

    search_for = ''
    if request.POST.has_key('search'):
        search_for = request.POST['search']
    
    if search_for != '':
        from lablog.utils.search import extract_words, build_query
        words = extract_words(search_for)
        
        query1 = build_query(words, ['activity_content', ])
        activities = Activity.objects.filter(query1).order_by("start_date")
        
        query2 = build_query(words, ['comment', ])
        birds = Bird.objects.filter(query2).order_by("date_of_birth")
        
        query3 = build_query(words, ['tags', ])
        tags = Bird.objects.filter(query3).order_by("date_of_birth")
    
        nbr_results = activities.__len__() + birds.__len__() + tags.__len__()
    
        _dict = {'activities': activities,
                'birds': birds,
                'tags': tags, 
                'nbr_results': nbr_results, 
                'search': words, }
    else:
        nbr_results = 0
        _dict = {}
                
    return direct_to_template(request, 'search_results.html', _dict)
        
        

# use this for unfinished views
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
def not_implemented(request, custom_section_id):
    """
    Handling unavailable content                                                               
    """

    c = RequestContext(request, {  
        'description': _(u"The function you requested is not available yet."),        
        'referer': reverse('index_birdlist'),                                
        'title': _(u"Function not available"),
        'section_id': custom_section_id or "homepage",
        'main_page': reverse('index_birdlist'),
    })

    t = loader.get_template('birdlist/basic/error.html')
    return HttpResponse(t.render(c), status=200)
    
def index_breeding(request):
    couplings = Coupling.objects.filter(separation_date=None).select_related().order_by('cage__name')
    # the empty breeding cages
    empty_breeding_cages = Cage.objects.get_empty_cages(function=Cage.FUNCTION_BREEDING)
    return direct_to_template(request, "birdlist/breeding_index.html",\
            { 'couplings': couplings, 'empty_breeding_cages': empty_breeding_cages, })

def index_birdcare(request):
    # also allow search for end_date s that are in the future
    open_experiments = Activity.objects.filter(Q(activity_type__name='Experiment') & Q(Q(end_date=None) | Q(end_date__gte=datetime.date.today()))).select_related()
    var_dict = { 'open_experiments': open_experiments, }
    return direct_to_template(request, "birdlist/birdcare_index.html", var_dict)

def index_stats(request):
    birds = Bird.objects.all().exclude(date_of_birth = None).order_by("-date_of_birth")
    counter = dict()
    for i in birds:
        iso_calendar = i.date_of_birth.isocalendar()
        this_year = str(iso_calendar[0])
        this_week = str(iso_calendar[1])
        if this_week.__len__() == 1:
            this_week = '0' + this_week
            
        this_date = this_year + " - " + this_week
        
        if counter.get(this_date):
            counter[this_date] = counter[this_date] + 1
        else:
            counter[this_date] = 1
    
    counter = sorted(counter.items(), reverse = True)
    return render_to_response('birdlist/stats_basic.html', \
                {'counter': counter, }, context_instance=RequestContext(request))


########################### POPUP CRAP #########################################
# wrapper for handlePopAdd needed below
def handlePopAddBirdlist(request, FormType, event_type, username=None):
    from songbird.views import handlePopAdd
    return handlePopAdd(request, FormType, 'birdlist', event_type, username)

# pop-up windows
from birdlist.forms.birdlist_formsets import BirdForm, CageForm
def popup_new_bird(request):
    return handlePopAddBirdlist(request, BirdForm, 'bird')

def popup_new_cage(request):
    return handlePopAddBirdlist(request, CageForm, 'cage')

