# modules used in most views
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template    
from django.shortcuts import get_object_or_404
from lablog.models import Event, Event_Type, Experiment
from lablog.utils.generic import order_and_sort, get_user_object
from lablog.utils.event_type import query_latest

# /^experiment/(?P<experiment_slug>[-\w]+)/event_type/
## show list of event types
from django.views.generic.list_detail import object_list
def index(request, username, experiment_slug, entries_per_page=10):

    order, sort_dir = order_and_sort(request, default='desc')
    vdict = query_latest(request.user, username, order)
    experiment = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)

    paginate_by = entries_per_page
    if entries_per_page == 0:
        paginate_by = vdict.get('nbr_events')

    # passing on 'sort_dir' doesn't really work with 'paginate_by'
    return object_list(request, queryset = vdict.get('event_types'),
        template_name = 'lablog/event_type/event_type_list.html', 
        paginate_by = int(entries_per_page), 
        template_object_name = 'event_type',
        extra_context = {'experiment': experiment, 
        				'nbr_entries_to_show': entries_per_page, 
        				'sort_direction': sort_dir, } )

# /event_type/
## redirect to experiment list of user in case the page is called without an experiment_id
def redirect_index(request, username):
    return HttpResponseRedirect(reverse('index_experiment', args=(username,)))

# /experiment/slug/event_type/TYPE/delete/
from django.views.generic.create_update import delete_object
def delete(request, username, experiment_slug, event_type_id):

    experiment = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)
    event_type = Event_Type.objects.filter(author__username__exact=username, id__exact=event_type_id)

    if event_type:
        return delete_object(request, model = Event_Type, 
                object_id = event_type_id, 
                login_required = True,
                post_delete_redirect = reverse('detail_experiment', args=(username, experiment.slug,)), 
                template_name = 'lablog/event_type/event_type_delete.html',
                extra_context = {'experiment': experiment, }, )
    else:
        return direct_to_template(request,'lablog/basic/access_error.html')


from lablog.forms.lablogforms import EventTypeForm
def edit(request, username, experiment_slug, event_type_id):
    query_list = get_object_or_404(Event_Type, author__username__exact=username, id__exact=event_type_id)
    experiment = get_object_or_404(Experiment, slug__exact=experiment_slug)

    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = EventTypeForm(username, request.POST, instance=query_list)
        # discard changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('index_event_type', args=(username, experiment_slug)))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            # create an instance of the form so we can save it later with
            # the new value
            form_instance = form.save(commit = False)
                            
            # save the instance    
            form_instance.save()
            
            # Redirect after POST
            return HttpResponseRedirect(reverse('index_event_type', args=(username, experiment_slug)))

    else:
        form = EventTypeForm(username, instance=query_list)

    pageContext = {'form': form, 'experiment': experiment, 'change': True, 'form_object_name': 'event_type'}
    return direct_to_template(request, 'event/forms/base_event_form.html', pageContext)

################################ " pop-up windows "

from lablog.views.basic.lablog_main import handlePopAddLablog
from songbird.views import handlePopEdit

def popup_new_EventType(request, username):
    return handlePopAddLablog(request, EventTypeForm, 'event_type', username)

def popup_edit_EventType(request, username, event_type_id):
    return handlePopEdit(request, EventTypeForm, Event_Type, username, 'event_type', event_type_id)

## EOF
