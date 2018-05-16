import datetime

from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.util import ErrorList

from lablog.models import Experiment, Protocol, Project, Event
from lablog.views.basic.lablog_main import not_implemented, server_error
from lablog.utils.generic import order_and_sort
from lablog.utils.experiment import *
from lablog.utils.generic import copy_data_from_request_set_author
from lablog.forms.lablogforms import EventFormQuick, TagEvent, ExperimentForm, ExperimentFormAddFromAnimalList

from birdlist.models import Activity

ANIMAL_DATABASE_KICKOFFDATE = datetime.date(2011, 1, 14)

## /experiment/
def index(request, username):
    nbr_return = 100
    vdict = query_latest(request.user, username, nbr_return)
    vdict.pop('experiments_in_animal_list')   
    return direct_to_template(request, 'experiment/experiment_list.html', vdict)

## show details for experiment
def detail(request, username, experiment_slug):

    query_object = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)

    phd_start_experiment = None
    bird_name, bird, phd_start_experiment, phd_end_experiment, activity_object = get_birdname_for_experiment(query_object)

    order, sort_dir = order_and_sort(request)

    "  show all events from all days by default.  "
    event_list = Event.objects.filter(experiment = query_object.pk, schedule = Event.SCHEDULE_PAST).select_related('event_type').order_by(order + 'date', order + 'time')
    event_list_todo = Event.objects.filter(experiment = query_object.pk).exclude(schedule = Event.SCHEDULE_PAST).select_related('event_type').order_by('-schedule', '-date', '-time')

    # we only show the last 10 entries
    event_list = event_list[:10]

    event_title = create_title(event_list, 'event', 'latest')
    event_todo_title = create_title(event_list_todo, 'event', 'planned')

    # quicklink for adding specific event type
    form = EventFormQuick(username)
    
    #  TagEvent(auto_id=False) won't work because the widget needs an ID!
    TagForm = TagEvent()

    betweenform = load_betweenform(username, query_object.pk)
    zipped, media_error_message = get_media_dirs(query_object)

    # offer 'merge' button to old experiments    
    PRE_DB_KICKOFF = None
    if query_object.start_date < ANIMAL_DATABASE_KICKOFFDATE:
        PRE_DB_KICKOFF = True
        
    my_dict = {'selected_object': query_object, 
		    'event_list': event_list, 
		    'bird_name': bird_name, 
		    'bird': bird,
		    'media_file_urls': zipped, 
		    'media_error_message': media_error_message, 
		    'betweenform': betweenform,
		    'form': form, 
		    'search_url': 1,
		    'event_title': event_title, 
		    'event_list_todo': event_list_todo, 
		    'event_todo_title': event_todo_title, 
		    'phd_start_experiment': phd_start_experiment, 
		    'phd_end_experiment': phd_end_experiment, 
		    'allow_user_sorting': 1, 
		    'TagForm': TagForm, 
		    'PRE_DB_KICKOFF': PRE_DB_KICKOFF, }        
        

    from songbird.utils import running_on_devserver
    if running_on_devserver(request):
        return direct_to_template(request,'experiment/experiment_object_detail.html', my_dict)
    else:
        try:		    
            return direct_to_template(request,'experiment/experiment_object_detail.html', my_dict)
        except:
            return server_error(request)


## edit selected experiment - new, with enabled birdlist synchronization
# problems:
# - can't change animal license and severity grade, since we ignore bird
# solution:
# - create two views - one for experiment with animal, one without.
def edit_form(request, username, experiment_slug):

    query_list = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)
    old_values = dict()
    old_values['title'] = query_list.title
    old_values['start_date'] = query_list.start_date
    old_values['end_date'] = query_list.end_date
    bird_name, bird, phd_start_experiment, phd_end_experiment, activity_object = get_birdname_for_experiment(query_list)

    # If the form has been submitted...
    if request.method == 'POST':
    
        # save changes
        if 'savebutton' in request.POST:
            form = ExperimentForm(username, request.POST, instance = query_list)

        # ignore changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, query_list.slug,)))
        
        # if form is valid.
        if form.is_valid():
            # save the experiment and return the new object
            bla = form.save()
            if bird_name:
                change_detected = None
                if bla.title != old_values['title']:
                    change_detected = True
                if bla.start_date != old_values['start_date']:
                    change_detected = True
                if bla.end_date != old_values['end_date']:
                    change_detected = True
                    
                if change_detected == True:
                    activity_object.activity_content = bla.title
                    activity_object.start_date = bla.start_date
                    activity_object.end_date = bla.end_date
                    activity_object.save()
                    print 'something changed!'
                    
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ExperimentForm(username, instance = query_list)

    return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
        'form': form, 'experiment': query_list, 'add': False, 
        'change': True, 'form_object_name': 'experiment', }
    )


'''
## edit selected experiment - old
def edit_form_old(request, username, experiment_slug):

    query_list = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)
    bird_name, bird, phd_start_experiment, phd_end_experiment, activity_object = get_birdname_for_experiment(query_list)

    # allow changing of birds for the moment
    # GenericFormSet = generate_bird_inline_form(username)
    
    ## NOT USED ANYMORE, because people can use the 'merge' button.
    ## allow assignment of bird, if none is assigned.
    #if bird_name == 'none':
    #    GenericFormSet = generate_bird_inline_form(username)
    #else:
    #    GenericFormSet = None
    #    formset = None

    GenericFormSet = None
    formset = None

    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = ExperimentForm(username, request.POST, instance = query_list)
            new_data = copy_experiment_fields_to_activity(request, username)
            if GenericFormSet:
                activity_object = get_activity_object(query_list)
                GenericFormSet = generate_bird_inline_form(username, 0)
                # DO NOT REMOVE! very important to keep activity in sync with 
                # experiment
                formset = GenericFormSet(new_data, instance = activity_object, prefix = 'bird')

        # generate form creating new object
        elif 'newbutton' in request.POST:
            form = ExperimentForm(username, request.POST)
            # FIX ME! - add GenericFormSet here. take a copy of the current bird
            # and generate a new formset with it.
            # for now we just disable this and redirect back to the experiment
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, query_list.slug,)))


        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, query_list.slug,)))
        
        # we either have a form only, or a form and a formset
        if (form.is_valid() and not formset) or (form.is_valid() and formset and formset.is_valid()):
            if new_data.has_key('bird-0-animal_experiment_licence') and (new_data['bird-0-animal_experiment_licence'] == '' and new_data['bird-0-bird'] != ''):
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append('No animal license selected')
                return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
                    'form': form, 'experiment': query_list, 'add': False, 
                    'change': True, 'form_object_name': 'experiment', 
                    'formset': formset}
                )

            # if animal is selected, make sure severity grade is selected too!
            if new_data.has_key('bird-0-severity_grade') and (new_data['bird-0-severity_grade'] == '' and new_data['bird-0-bird'] != ''):
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append('No severity grade selected')
                return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
                    'form': form, 'experiment': query_list, 'add': False, 
                    'change': True, 'form_object_name': 'experiment', 
                    'formset': formset}
                )


            # save the experiment and return the new object
            bla = form.save()
            print bla

            # in case we also have a formset
            if formset:
                # return the just created experiment
                experiment = Experiment.objects.get(id = bla.id)

                # save the bird inline data
                fill_activity_formset_with_data_from_experiment(formset, experiment)
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ExperimentForm(username, instance = query_list)
        # generate the final formset
        if GenericFormSet:
            activity_object = get_activity_object(query_list)
            # generate an extra form, if no bird is associated.
            extra_form = 1
            if activity_object:
                extra_form = 0

            GenericFormSet = generate_bird_inline_form(username, extra_form)
            formset = GenericFormSet(instance = activity_object, prefix = 'bird')



    return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
        'form': form, 'experiment': query_list, 'add': False, 
        'change': True, 'form_object_name': 'experiment',
        'formset': formset, }
    )
'''


## create new experiment - including the optional animal
# Problems: 
# - formset does not get error checked
# - if there's an error with the experiment form, formset won't appear
# - very messy error checking for formset after is_valid() call.
#
# Solutions:
# - create one form which contains Experiment + Activity?
# - create model form for Experiment and add fields necessary for activity
# - use wizard and let user select whether he / she wants to add animal 
#   (needs one additional click)
#

''' work in progress

    FormWizard only works with "Form classes" in django 1.2 & 1.3
    But we need "ModelForm" classes, which only work with django 1.4

from lablog.utils.experiment import new_experiment_with_animal_wizard
from birdlist.forms.activity_forms import ActivityFormAddExperimentFromLablog
from lablog.forms.lablogforms import ExperimentFormBasic
def new_experiment_with_bird(request, username):

    form_list = [ExperimentFormBasic, ActivityFormAddExperimentFromLablog]
    form = new_experiment_with_animal_wizard(form_list)
    # indicate that there are optional steps in the form, so the number of steps 
    # is not fixed.
    optional_steps = True
    mydict = { 'username': username,
               'form_list_orig': form_list, 'optional_steps': optional_steps, }
    return form(context = RequestContext(request), request = request, extra_context = mydict)


''' 
from lablog import signals
def new_experiment_with_bird(request, username):

    GenericFormSet = generate_bird_inline_form(username)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'newbutton' in request.POST:

            new_data = copy_data_from_request_set_author(request, username)
            form = ExperimentForm(username, new_data)
            formset = None
            if new_data.has_key('bird-0-bird') and new_data['bird-0-bird']: # evaluate formset if user choose a bird
                formset = generate_activity_formset_with_POST_data_from_experiment(request, username, GenericFormSet)

            # manually evoke signal.
            # signals.experiment_mod.send(sender=Experiment, author=request.user.username, title=new_data['title'])
            
        # return to experiment index
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('index_experiment', args=(username, )))
        
        if form.is_valid() and ((formset != None and formset.is_valid()) or formset == None):
            
            # if animal is selected, make sure animal license is selected too!
            if new_data.has_key('bird-0-animal_experiment_licence') and (new_data['bird-0-animal_experiment_licence'] == '' and new_data['bird-0-bird'] != ''):
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append('No animal license selected')
                return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
                    'form': form, 'experiment': '', 'add': True, 
                    'change': False, 'form_object_name': 'experiment', 
                    'formset': formset}
                )
                
            # if animal is selected, make sure severity grade is selected too!
            if new_data.has_key('bird-0-severity_grade') and (new_data['bird-0-severity_grade'] == '' and new_data['bird-0-bird'] != ''):
                errors = form._errors.setdefault("__all__", ErrorList())
                errors.append('No severity grade selected')
                return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
                    'form': form, 'experiment': '', 'add': True, 
                    'change': False, 'form_object_name': 'experiment', 
                    'formset': formset}
                )                
                

            # save the experiment and return the new object
            bla = form.save()

            # return the just created experiment
            experiment = Experiment.objects.get(id = bla.id)

            # save the bird inline data
            if formset:
                fill_activity_formset_with_data_from_experiment(formset, experiment)
                        
            # Redirect after POST to new experiment entry
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))
                
    # Form has been called - user can fill it out.
    else:
        ''' formset approach - breakes custom widgets.
        from django.forms.models import modelformset_factory
        ExperimentFormset = modelformset_factory(Experiment, extra=1)
        formset = ExperimentFormset(queryset = Experiment.objects.none())
        form = ''
        '''
        
        form = ExperimentForm(username)
        # generate the final formset
        formset = GenericFormSet(prefix = 'bird')

        #for form in formset.forms:
        #	print form.as_p()


    return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
        'form': form, 'experiment': '', 'add': True, 
        'change': False, 'form_object_name': 'experiment', 
        'formset': formset}
    )
#'''

## delete experiment
def delete(request, username, experiment_slug):

    experiment = get_object_or_404(Experiment, slug__exact=experiment_slug, author__username = username)
    
    # this is a list of events, so get_object_or_404 will not work!
    event_list = Event.objects.filter(experiment__exact=experiment.id)

    # check if user really wants to delete this experiment
    if request.method == 'GET':
        return direct_to_template(request, 'experiment/experiment_object_delete.html', {'event_list': event_list, 'experiment': experiment, })
    
    # look at user response
    if request.method == 'POST':
        
        # delete the experiment & all events that come with it
        if 'deletebutton' in request.POST:
            event_list.delete()
            # we can remove the call to this method, once the upstream bug has 
            # been fixed: http://code.djangoproject.com/ticket/6870
            remove_animal_list_link_from_experiment(experiment.id)
            experiment.delete()

        # return to experiment index
        return HttpResponseRedirect(reverse('index_experiment', args=(username, )))


# /experiment/slug/generic/
""" playing around with generic views """        
from django.views.generic.list_detail import object_detail
def detail_generic(request, username,  experiment_slug):

    """ different users might use the same slug, so we need to get all 
        experiments for the current user 
    """
    experiment = Experiment.objects.filter(author__username__exact=username)
    return object_detail(request, queryset = experiment, slug = experiment_slug, 
        template_name = 'lablog/experiment/detail.html')

# /experiment/slug/search/
def search(request, username, experiment_slug):

    terms = request.POST['terms']
    
    from lablog.utils.search import extract_words, build_query
    words = extract_words(terms)
    
    query1 = build_query(words, ['text_field', ])
    events = Event.objects.filter(query1, author__username__exact = username, experiment__slug__exact = experiment_slug)
    nbr_results = events.__len__()

    return direct_to_template(request, 'basic/search_results.html', {
        'nbr_results': nbr_results, 'search': words, 'events': events}
    )

# /experiment/slug/list/
def list_events(request, username, experiment_slug, entries_per_page=10, event_type_id=None, year=None, month=None, day=None):

    experiment, events = get_all_events(request, username, experiment_slug, event_type_id, year, month, day)
    nbr_events = events.__len__()

    return return_event_list_object(request, username, events, entries_per_page, experiment, nbr_events, event_type_id)

# /experiment/slug/list/all/
def list_all_events(request, username, experiment_slug, event_type_id=None, year=None, month=None, day=None):

    experiment, event_list = get_all_events(request, username, experiment_slug, event_type_id, year, month, day)
    entries_per_page = event_list.__len__()

    return list_events(request, username, experiment_slug, entries_per_page, event_type_id, year, month, day)

# /experiment/slug/list/between/some_event
def list_events_between(request, username, experiment_slug, event_type_id=None, year=None, month=None, day=None):

    nothing_found = 'No events found for this event type. Please modify your selection.'

    experiment, event_list_all = get_all_events(request, username, experiment_slug, None, year, month, day)

    if not event_type_id:
        event_list_all = event_list_all.filter(id = 0)
        return return_event_list_object(request, username, event_list_all, 0, experiment, 0, event_type_id, nothing_found)

    experiment, event_list_sub = get_all_events(request, username, experiment_slug, event_type_id, year, month, day)

    ' analyze event lists '
    subselected = []
    nbr_entries = event_list_sub.__len__()

    # make sure to exit if no event was found
    if nbr_entries == 0:
        return return_event_list_object(request, username, event_list_sub, 0, experiment, 0, event_type_id, nothing_found)

    # is this a paired event (on&off define a block) or a single event?
    from lablog.models import Event_Type
    paired = 1
    if Event_Type.objects.get(id__exact = event_list_sub[0].event_type_id).flag_meaning.upper().__eq__('NONE'):
        paired = 0

    # how many pairs are we looking at? 
    if paired == 1:
        # in case of an uneven number of entries, we add one
        nbr_pairs = nbr_entries / 2
        if nbr_entries.__mod__(2) == 1:
            nbr_pairs = nbr_pairs + 1
    # unpaired events
    else:
        if nbr_entries == 1:
            nbr_pairs = 1
        else:
            nbr_pairs = nbr_entries - 1

    offset = 0
    # in case of paired events, make sure the first entry is a STOP entry, 
    # otherwise ignore the first entry. this is obviously a very crude fix,
    # because the user might have forgotten many stops along the way (or starts)
    if paired == 1 and event_list_sub[0].flag_box == 0:
            offset = 1

    ' extract events '
    for i in xrange(nbr_pairs):

        i1 = i
        if paired == 1:
            i1 = 2 * i + offset

        i2 = i1 + 1
        if nbr_entries == 1:
            i1 = 0;
            i2 = i1

        # if offset == 1, then we might go beyond the end index
        if i1 == nbr_entries or i2 == nbr_entries:
            break

        stop_time = event_list_sub[i1].time
        start_time = event_list_sub[i2].time
        this_date = event_list_sub[i1].date
        # only look for block on the same day. don't look for events across days
        these_entries = event_list_all.filter(time__range = (start_time, stop_time), date__exact = this_date)
        if these_entries.__nonzero__():
            for j in these_entries:
                subselected.append(j.id.__int__())

    
    subselected = sorted(subselected)
    all_events = event_list_all.filter(id__in = subselected)
    events = all_events
    entries_per_page = all_events.__len__()
    nbr_events = events.__len__()

    return return_event_list_object(request, username, all_events, entries_per_page, experiment, nbr_events, event_type_id)

# /experiment/slug/list/between/
def list_events_between_start(request, username, experiment_slug):

    if request.method == 'POST':

        event_type_id = request.POST['event_type']
        # none selected?
        if not event_type_id:
            event_type_id = 0

        if 'ShowSelectedOnly' in request.POST:
            return HttpResponseRedirect(reverse('list_all_events', args=(username, experiment_slug, event_type_id)))

    else:
        event_type_id = 0

    return HttpResponseRedirect(reverse('list_events_between', args=(username, experiment_slug, event_type_id)))


#/ experiment/import_from_animal_list/
def import_from_animal_list(request, username):

    activity_id = None
    new_data = request.POST.copy()
    if new_data.has_key('activity_id'):
        activity_id = new_data['activity_id']

    if not activity_id or 'cancelbutton' in new_data:
        return HttpResponseRedirect(reverse('index_experiment', args=(username, )))

    if 'newbutton' in new_data:
        new_data = copy_data_from_request_set_author(request, username)
        form = ExperimentFormAddFromAnimalList(activity_id, username, new_data)

        if form.is_valid():
            # find the activity that already exists in the animal database
            present_activity = Activity.objects.get(id = activity_id)
        
            # create experiment & save it - otherwise we lose the protocol info.
            experiment = form.save()
            
            # now overwrite false defaults with values from activity. 
            
            # ideally, we want to clean up the old experiment titles, however
            # this will brake synchronization.
            # experiment.title = present_activity.get_activity_content_pretty()
            experiment.title = present_activity.activity_content
            experiment.start_date = present_activity.start_date
            experiment.end_date = present_activity.end_date
            # don't override the user given plan.
            #experiment.plan = present_activity.bird.name
            
            # Save updated experiment
            experiment.save()
            
            # link activity to experiment & save activity
            present_activity.content_object = experiment
            present_activity.save()
            
            return HttpResponseRedirect(reverse('index_experiment', args=(username, )))
            
    elif 'import into lablog' in new_data:
        form = ExperimentFormAddFromAnimalList(user=username, activity_id=activity_id)
        
    return direct_to_template(request, 'experiment/forms/base_experiment_form.html', {
        'form': form, 'experiment': '', 'add': True, 
        'change': False, 'form_object_name': 'experiment', }
    )

# r'^experiment/possible_imports_from_animal_list/    
def possible_imports_from_animal_list(request, username):
    nbr_return = 10000
    vdict = query_latest(request.user, username, nbr_return)
    vdict.pop('experiments')
    vdict.pop('active_experiments')
    vdict.pop('finished_experiments')            
    return direct_to_template(request, 'experiment/experiment_list.html', vdict)
    
    

''' merge old lablog experiments with birdlist entries '''

from django.template import RequestContext
from birdlist.forms.birdlist_formsets import FindBirdForm, FindExperimentForm
from lablog.utils.experiment import merge_exp_form

#^experiment/merge_experiment_with_animal_list/$'
def merge_experiment_with_animal_list(request, username, experiment_slug):
    form = merge_exp_form([FindBirdForm, FindExperimentForm])
    experiment = get_object_or_404(Experiment, author__username__exact = username, slug__exact = experiment_slug)
    exp_title = experiment.title
    mydict =    {   'username': username, 'exp_slug': experiment_slug, 
                    'exp_title': exp_title, 'experiment': experiment, 
                }
    return form(context=RequestContext(request), request=request, extra_context=mydict)



