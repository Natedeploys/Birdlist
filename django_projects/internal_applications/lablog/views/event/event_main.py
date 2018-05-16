# modules used in most views
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template    
from django.shortcuts import get_object_or_404
from lablog.models import Event, Event_Type, Experiment
from lablog.utils.generic import get_user_object
from lablog.forms.lablogforms import EventForm

## we don't have any event listings, redirect to experiment list of user
def index(request, username):

    return HttpResponseRedirect(reverse('index_experiment', args=(username,)))


## show details for event
def detail(request, username, event_id):
    
    query_object = get_object_or_404(Event, id__exact=event_id)
    experiment = get_object_or_404(Experiment, event__exact=event_id)

    return direct_to_template(request,'event/event_object_detail.html', {'selected_object': query_object, 'experiment': experiment})


## delete event
def delete(request, username, event_id):

    experiment = get_object_or_404(Experiment, event__exact=event_id)
    query_object = get_object_or_404(Event, id__exact=event_id)

    # check if user really wants to delete this event
    if request.method == 'GET':
        return direct_to_template(request, 'event/event_object_delete.html', {'experiment': experiment, 'event': query_object, })
    
    # look at user response
    if request.method == 'POST':
        
        # delete event because user requested this.
        if 'deletebutton' in request.POST:
            query_object.delete()

        # return to experiment
        return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))
    

## edit selected event
def edit_form(request, username, event_id):
    
    query_list = get_object_or_404(Event, author__username__exact=username, id__exact=event_id)
    experiment = get_object_or_404(Experiment, event__exact=event_id)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = EventForm(username, request.POST, instance=query_list)
        # generate form creating new object
        elif 'newbutton' in request.POST:
            form = EventForm(username, request.POST)
        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_event', args=(username, query_list.id,)))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            # create an instance of the form so we can save it later with
            # the new value
            form_instance = form.save(commit = False)
        
            # set the author field correctly in case this is a new object
            if 'newbutton' in request.POST:
            
                user_object = get_user_object(username)
               
                # set the author field
                form_instance.author = user_object
                
            # save the instance    
            form_instance.save()
            
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))

    else:
        form = EventForm(username, instance=query_list)

    return direct_to_template(request, 'event/forms/base_event_form.html', {
        'form': form, 'experiment': experiment, 'add': True, 'change': True, 'form_object_name': 'event'}
    )


## create new event - basically the same as edit_form
def new(request, username, experiment_id=None):

    experiment = ''
    if experiment_id is not None:
        experiment = get_object_or_404(Experiment, id__exact=experiment_id)
    
    # If the form has been submitted; I also abuse this in the experiment view
    # therefore the "AddEvent" check, see below for details.
    if request.method == 'POST' and 'AddAndEditEvent' not in request.POST:
    
        # revert changes
        if 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))

        if 'AddAndSaveEvent' in request.POST:
            experiment = Experiment.objects.get(id__exact=experiment_id)
            post_values = request.POST.copy()
            post_values.appendlist('experiment', experiment.id)
            form = EventForm(username, post_values)

        elif 'newbutton' in request.POST:
            # generate form creating new object, 'newbutton' and other cases
            form = EventForm(username, request.POST)
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            # create an instance of the form so we can save it later with
            # the new value
            form_instance = form.save(commit = False)

            # set the author field correctly in case this is a new object
            user_object = get_user_object(username)
            # set the author field
            form_instance.author = user_object        

            # new button is used either with or with out experiment_id in the URL
            if 'newbutton' in request.POST and experiment_id is not None:
                form_instance.experiment = experiment
            # not in the URL -> but in the request object
            else:
                experiment = Experiment.objects.get(id__exact=form_instance.experiment.id)
                
            # save the instance    
            form_instance.save()
            
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))
                
                
    # new form request, or event_type submitted through the experiment detail page
    else:
        event_type_id = None
        flag_box = False
        schedule = Event.SCHEDULE_PAST
        if 'AddAndEditEvent' in request.POST:
            event_type_id = request.POST['event_type']
            schedule = request.POST['schedule']
            # flag_box will only be passed on, if it's selected
            if 'flag_box' in request.POST:
                flag_box = request.POST['flag_box']

        form = basic_event_form(username, experiment_id, event_type_id, flag_box, schedule)


    return direct_to_template(request, 'event/forms/base_event_form.html', {
        'form': form, 'experiment': experiment, 'add': True, 'change': False, 'form_object_name': 'event'}
    )


def basic_event_form(username, experiment_id=None, event_type_id=None, flag_box=False, schedule = 1):

    import time
    form = EventForm(username)

    form.fields['event_type'].initial = event_type_id
    form.fields['flag_box'].initial = flag_box
    form.fields['date'].initial = time.strftime("%Y-%m-%d", time.localtime())
    form.fields['time'].initial = time.strftime("%H:%M:%S", time.localtime())
    form.fields['schedule'].initial = schedule

    if experiment_id is not None:
        # preselect the experiment field to the currently selected experiment
        experiment = Experiment.objects.get(id__exact=experiment_id)
        form.fields['experiment'].initial = experiment.id

    return form


def convert_event_list_to_seconds_since_epoch(event_list):
    ' convert the event list  '

    from lablog.utils.generic import convert_date_time_to_seconds_since_epoch

    # define empty list
    time_in_secs = []
    # extract the date and time for each event
    bla = event_list.values('date', 'time')

    for i in bla:
        # take an entry
        blub = i.values()
        # convert entry to seconds and append to list
        time_in_secs.append(convert_date_time_to_seconds_since_epoch(blub[0], blub[1]))

    return time_in_secs

# /event/(?P<event_id>[-\w]+)/tag/
## add tag to event
def tag(request, username, event_id):
    experiment = get_object_or_404(Experiment, event__exact=event_id)
    tag_name = request.POST.get('tag')
    current_url = request.POST.get('current_url')

    if not tag_name:
        return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))

	# this event        
    query_object = get_object_or_404(Event, id__exact=event_id)

    # add new tag - if user tries to submit multiple tags, then we have a problem.
    from lablog.utils.generic import tag_object
    # multiple tags (if provided) are assumed to be separated by a komma.
    tags = tag_name.split(',')
    for i in tags:
        if i == " ": # split() above might return us an empty string.
            continue
        tag_object(query_object, '"%s"' % i)
    
    if current_url:
        return HttpResponseRedirect(current_url)
    else:
        return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))

# /event/(?P<event_id>[-\w]+)/tag/(?P<tag_id>\d+)/delete/
## remove tag from event
def delete_tag(request, username, event_id, tag_id):
    # this experiment & event
    experiment = get_object_or_404(Experiment, event__exact=event_id)
    query_object = get_object_or_404(Event, id__exact=event_id)
    
    # delete the tag from the list of tags
    from tagging.models import Tag
    tag_name = Tag.objects.get(id__exact=tag_id)
    Tag.objects.update_tags(query_object, ' '.join(map(lambda s: '"%s"' % s, Tag.objects.get_for_object(query_object).exclude(name=tag_name).values_list('name'))))
    
    # explicitly sync the field of the event model with the new tags
    from lablog.utils.event import sync_tags_with_event
    sync_tags_with_event(Tag, query_object)
    
    return HttpResponseRedirect(reverse('detail_experiment', args=(username, experiment.slug,)))

## EOF

