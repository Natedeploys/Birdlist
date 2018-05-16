from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from birdlist.models import Activity, Bird, Activity_Type
from birdlist.forms.activity_forms import ActivityForm, ActivityFormExperiment, ActivityFormHealthStatus
from birdlist.utils.activity import close_experiment_wizard

def index(request):
    '''
    '''
    return direct_to_template(request, 'activity_index.html')


def activity_detail(request, activity_id):
    '''
    '''
    activity = Activity.objects.get(id=activity_id)

    return direct_to_template(request, 'birdlist/activity_detail.html',\
            {'activity': activity})


''' close activity / experiment '''
from django.template import RequestContext
from django.core.urlresolvers import reverse
from birdlist.forms.activity_forms import ActivityFormExperimentClose, ActivityFormExperimentCheckIfSongRecorded, ActivityFormExperimentCheckNbrSyls, ActivityFormExperimentCloseHideCheckoutOption
from birdlist.forms.birdlist_formsets import CheckoutAnimalFromColonyFormShort
from birdlist.utils.activity import allow_checkout_from_db

#^activity/(?P<activity_id>\d+)/close/
def activity_close(request, activity_id):
    ''' activity close view - works currently for experiments only '''

    activity = Activity.objects.get(id = activity_id)
    if activity.activity_type.name != activity.EXPERIMENT_STRING:
        return HttpResponseRedirect(reverse('bird_overview', args=(activity.bird.id, )))
    
    # pick the correct forms.
    if allow_checkout_from_db(request, activity.bird) == False:
        form_list = [ActivityFormExperimentCloseHideCheckoutOption, ActivityFormExperimentCheckIfSongRecorded, ActivityFormExperimentCheckNbrSyls]
    else:
        form_list = [ActivityFormExperimentClose, ActivityFormExperimentCheckIfSongRecorded, ActivityFormExperimentCheckNbrSyls, CheckoutAnimalFromColonyFormShort]
    
    form = close_experiment_wizard(form_list)
    # indicate that there are optional steps in the form, so the number of steps 
    # is not fixed.
    optional_steps = True
    mydict = { 'activity': activity, 'bird': activity.bird, 
                'form_list_orig': form_list, 'optional_steps': optional_steps, }
    return form(context = RequestContext(request), request = request, extra_context = mydict)


def activity_edit(request, activity_id):
    '''
    '''
    activity = get_object_or_404(Activity, id=activity_id)
    activity_type_name = activity.activity_type.name

    # hack to redirect to specific VIEW ONLY urls
    #
    # 1st problem: - DONE
    # this is necessary, because we are lazy in templates like 'activity_list_include.html'
    # where we call "act.get_edit_url". get_edit_url should do the necessary
    # checks so that we don't need to do the checks here.
    #
    # 2nd problem: - PARTIALLY DONE - left comment in models.py
    # we do 'hard' lookups by name, i.e., 'Cage Transfer', 'Reservation', what 
    # happens if someone renames these? we run into trouble. The same is true for
    # the code in "activity_detail.html".
    #
    # 3rd problem: - DONE - ignored
    # in case we want to fix all of above problems with fixing get_edit_url,
    # we'll have to pass request.user.username to it, because we need it for the
    # the last check in the following list.
    #
    # Because of above problems, we need to check here manually for all 
    # CHECKFORPERMISSIONS cases. The remaining cases are taken care of by 
    # get_edit_url() in models.py.
    if (activity_type_name in activity.CHECKFORPERMISSIONS and not (request.user.username == activity.originator.username)):
        return HttpResponseRedirect(activity.get_absolute_url(), )
    
    prev = ''
    if request.GET.has_key('prev'):
        prev = request.GET['prev']
        
    if request.POST.has_key('prev'):
        prev = request.POST['prev']

    if request.method == 'POST':

        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(activity.bird.get_absolute_url(), )

        if 'savebutton' in request.POST:
            
            if activity_type_name == activity.EXPERIMENT_STRING:
                form = ActivityFormExperiment(request.POST, instance=activity)
            if activity_type_name == activity.HEALTH_STATUS_STRING:
                form = ActivityFormHealthStatus(request.POST, instance=activity)

            if form.is_valid():
                form.save()
                if prev:
                    return HttpResponseRedirect(prev)
                else:
                    return HttpResponseRedirect(activity.bird.get_absolute_url(), )

            else:
                return direct_to_template(request,
                        'birdlist/forms/activity_edit.html',
                        {'form': form, 'activity': activity, 'change': True, 'prev': prev, })

    else:
        if activity_type_name == activity.EXPERIMENT_STRING:
            form = ActivityFormExperiment(instance=activity)
        elif activity_type_name == activity.HEALTH_STATUS_STRING:
            form = ActivityFormHealthStatus(instance=activity)
        else:
            form = ActivityForm(instance=activity)


    return direct_to_template(request, 'birdlist/forms/activity_edit.html',
            {'form': form, 'activity': activity, 'change': True, 'prev': prev, })


# /birdlist/activity/add_experiment/?bird_id=1185
def add_experiment(request):
    '''
    '''
    # called in templates/bird_overview.html
    if request.method == 'GET':

        bird_id = request.GET.get('bird_id')
        bird = get_object_or_404(Bird, id=bird_id)

        activity_type = Activity_Type.objects.filter(name='Experiment')[0]
        activity = Activity(bird=bird, activity_type=activity_type)

        form = ActivityFormExperiment(instance=activity)

        return direct_to_template(request,
                        'birdlist/forms/activity_edit.html',
                        {'form': form, 'activity': activity, 'change': True, })

    elif request.method == 'POST':

        form_data = request.POST.copy()
        form_data['originator'] = request.user.id 

        form = ActivityFormExperiment(form_data)
        bird = Bird.objects.get(id=int(form_data['bird']))

        if 'cancelbutton' in form_data:
            return redirect(bird) 

        if 'savebutton' in form_data:
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(bird.get_absolute_url(), )
            else:
                return direct_to_template(request,
                        'birdlist/forms/activity_edit.html',
                        {'form': form, 'change': True, })

    # why 'else' here? request.method is 'GET' or 'POST', can't be anything else
    else:
        redirect('birdlist/')


# /birdlist/activity/add_healthstatus/?bird_id=1185
def add_healthstatus(request):
    '''
    '''
    # called in templates/bird_overview.html
    if request.method == 'GET':

        bird_id = request.GET.get('bird_id')
        bird = get_object_or_404(Bird, id=bird_id)

        activity_type = Activity_Type.objects.filter(name='Health Status')[0]
        activity = Activity(bird=bird, activity_type=activity_type)

        form = ActivityFormHealthStatus(instance=activity)

        return direct_to_template(request,
                        'birdlist/forms/activity_edit.html',
                        {'form': form, 'activity': activity, 'change': True, })

    elif request.method == 'POST':

        form_data = request.POST.copy()
        form_data['originator'] = request.user.id
        form_data['severity_grade'] = Activity.SEVERITY_NONE

        form = ActivityFormHealthStatus(form_data)
        bird = Bird.objects.get(id=int(form_data['bird']))

        if 'cancelbutton' in form_data:
            return redirect(bird) 

        if 'savebutton' in form_data:

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(bird.get_absolute_url(), )

            else:
                return direct_to_template(request,
                        'birdlist/forms/activity_edit.html',
                        {'form': form, 'change': True, })
                        
    # why 'else' here? request.method is 'GET' or 'POST', can't be anything else                
    else:
        redirect('birdlist/')
