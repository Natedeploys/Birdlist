from django.views.generic.simple import direct_to_template
from django.contrib.auth import authenticate
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from lablog.models import Experiment, Project, Event, Event_Type, Note


def labloglogin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index_user', args=(request.user.username, )))
    else:
        return login(request, template_name = 'lablog/basic/login.html' )


def start(request):
    ''' View for entrance page of lablog.
    '''
    # redirect user to personal start page if logged in
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index_user', args=(request.user.username, )))

    # otherwise send them to the login page      
    else:
        return HttpResponseRedirect(reverse('labloglogin'))


def index_user(request, username):

    from lablog.views.experiment import experiment_main
    vdict_exp = experiment_main.query_latest(request.user, username)

    from lablog.views.project import project_main
    vdict_proj = project_main.query_latest(request.user, username, 5)

    #latest_projects = Project.objects.filter(author=request.user.id).order_by('-start_date')[:5]

    event_list = Event.objects.filter(author=request.user.id, schedule = Event.SCHEDULE_PAST).select_related('event_type').order_by('-date', '-time')[:5]
    event_list_todo = Event.objects.filter(author=request.user.id).exclude(schedule = Event.SCHEDULE_PAST).select_related('event_type').order_by('-date', '-time')[:5]
    number_todo =  event_list_todo.__len__()
    event_todo_title  = 'No scheduled events found'

    if number_todo != 0:
        event_todo_title  = "Next things ToDo (Events)"

    notes = Note.objects.filter(author=request.user.id, schedule = Note.SCHEDULE_PAST).order_by('-date')[:5]
    notes_todo = Note.objects.filter(author=request.user.id).exclude(schedule = Note.SCHEDULE_PAST).order_by('-date')[:5]

    last_logins = User.objects.all().order_by('-last_login')


    nbr_event_list = event_list.__len__()
    nbr_event_list_todo = number_todo
    nbr_notes = notes.__len__()
    nbr_notes_todo = notes_todo.__len__()
    projects = vdict_proj['projects']
    experiments = vdict_exp['experiments']
    
    new_user = 0
    if (nbr_event_list == 0 and nbr_notes == 0) or projects == False or experiments == False:
        new_user = 1
    

    vdict = {   'event_list': event_list,  
                'event_list_todo': event_list_todo,
                'event_todo_title': event_todo_title, 
                'notes': notes,
                'notes_todo': notes_todo,   
                'last_logins': last_logins, 
                'new_user': new_user, 
    }

    vdict.update(vdict_exp)
    vdict.update(vdict_proj)
    vdict.pop('finished_experiments')
    vdict.pop('finished_projects')
    vdict.pop('experiments_in_animal_list')    

    return direct_to_template(request, 'lablog/basic/lablog_main.html', vdict)


from tagging.views import tagged_object_list
from tagging.utils import get_tag
def show_user_tags(request, username, tag=None):
    queryset = Event.objects.filter(author=request.user.id)
    if tag == None:
        return HttpResponseRedirect(reverse('index_lablog'))
    else:
        return tagged_object_list(request, queryset, tag, paginate_by=25,
            allow_empty=True, template_name='lablog/basic/tags.html')

def active_inactive_objects(objectlist, nbr_return=10):

    active_objects = objectlist.filter(end_date=None).order_by('-start_date')[:nbr_return]
    finished_objects = objectlist.exclude(end_date=None).order_by('-start_date')[:nbr_return]
    objects = (active_objects.count() > 0) | (finished_objects.count() > 0)

    return active_objects, finished_objects, objects


def index_help(request, username):
    """
	    Show lablog help
    """
    return direct_to_template(request, 'lablog/basic/help_main.html')



from songbird.views import generic_server_error, generic_not_implemented
def server_error(request):
    """
    Handling Error 500.                                                                  
    """
    return generic_server_error(request, reverse('index_lablog'))


def not_implemented(request, custom_section_id):
    """
    Handling unavailable content                                                               
    """
    return generic_server_error(request, custom_section_id, reverse('index_lablog'))


### wrapper for handlePopAdd ###################################################

def handlePopAddLablog(request, FormType, event_type, username):
    from songbird.views import handlePopAdd
    return handlePopAdd(request, FormType, 'lablog', event_type, username)

################################ " pop-up windows " ############################
from lablog.forms.lablogforms import ProjectForm, ProtocolForm, ExperimentForm
def popup_new_Experiment(request, username):
    return handlePopAddLablog(request, ExperimentForm, 'experiment', username)

def popup_new_Project(request, username):
    return handlePopAddLablog(request, ProjectForm, 'project', username)
    
def popup_new_Protocol(request, username):
    return handlePopAddLablog(request, ProtocolForm, 'protocol', username)



### ajax form test

from django.http import HttpResponse
from django.core import serializers
from lablog.models import Experiment

def xhr_test(request, username, format):
    if request.is_ajax():
        if format == 'xml':
            mimetype = 'application/xml'
        if format == 'json':
            mimetype = 'application/javascript'
        data = serializers.serialize(format, Experiment.objects.all())
        return HttpResponse(data,mimetype)
    # If you want to prevent non XHR calls
    else:
        message = "No XHR"
        return HttpResponse(message)
        #return HttpResponse(status=400)


