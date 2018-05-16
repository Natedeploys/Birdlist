from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from lablog.models import Project
from lablog.forms.lablogforms import ProjectForm
    
## show all projects
def index(request, username):

    nbr_return = 100
    vdict = query_latest(request.user, username, nbr_return)
    return direct_to_template(request, 'project/project_list.html', vdict)

## look up methods for all projects - can be used in different views as well.
def query_latest(user, username, nbr_return=10):

    latest_projects = Project.objects.select_related().filter(author__username__exact=user)

    from lablog.views.basic.lablog_main import active_inactive_objects
    active_projects, finished_projects, projects = active_inactive_objects(latest_projects, nbr_return)

    vdict = {
        'projects': projects,
        'active_projects': active_projects,
        'finished_projects': finished_projects,
    }

    return vdict


## show details for project
def detail(request, username, project_slug):
    query_object = get_object_or_404(Project, author__username__exact=username, slug__exact=project_slug)
        
    from lablog.models import Note
    notes = Note.objects.filter(project = query_object.pk, schedule = Note.SCHEDULE_PAST).order_by('-date')[:100]
    notes_todo = Note.objects.filter(project = query_object.pk).exclude(schedule = Note.SCHEDULE_PAST).order_by('-date')[:100]

    from lablog.models import Experiment
    experiments = Experiment.objects.filter(project = query_object.pk).order_by('-data', '-start_date')[:100] 
       
    return direct_to_template(request, 'project/project_detail.html', 
        {'selected_object': query_object, 
        'search_url': 1,
        'search_project': 1,
        'notes': notes, 
        'experiments': experiments, 
        'notes_todo': notes_todo, })


## lookup project by ID and redirect to project by slug. This is retarded & very
## expensive because we have one additional lookup ...
def lookup(request, username, project_id):
    query_list = Project.objects.get(id__exact=project_id)
    return HttpResponseRedirect(reverse('detail_project', args=(username, query_list.slug)))


## edit the selected project
def edit_form(request, username, project_slug):

    query_list = get_object_or_404(Project, author__username__exact=username, slug__exact=project_slug)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = ProjectForm(username, request.POST, instance=query_list)
        # generate form creating new object
        elif 'newbutton' in request.POST:
            form = ProjectForm(username, request.POST)
        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_project', args=(username, query_list.slug,)))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            form.save()
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_project', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ProjectForm(username, instance=query_list) # An unbound form

    return direct_to_template(request, 'project/forms/base_project_form.html', {
        'form': form, 'project': query_list, 'add': False, 'change': True, 'form_object_name': 'project'}
    )


## create new project
def new(request, username):
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'newbutton' in request.POST:

            from lablog.utils.generic import copy_data_from_request_set_author
            new_data = copy_data_from_request_set_author(request, username)
            form = ProjectForm(username, new_data)
            
        # return to experiment index
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('index_project', args=(username, )))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            form.save()
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_project', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ProjectForm(username) # An unbound form

    return direct_to_template(request, 'project/forms/base_project_form.html', {
        'form': form, 'project': '', 'add': True, 'change': False, 'form_object_name': 'project'}
    )


## delete project
def delete(request, username, project_slug):

    project = get_object_or_404(Project, author__username__exact=username, slug__exact=project_slug)

    # check if user really wants to delete this project
    if request.method == 'GET':
        return direct_to_template(request, 'project/project_object_delete.html', {'project': project, })
    
    # look at user response
    if request.method == 'POST':

        from lablog.models import Note
        # this is a list of notes, so get_object_or_404 will not work!
        note_list = Note.objects.filter(project__exact=project.id)
        
        from lablog.utils.experiment import remove_animal_list_link_from_experiment
        from lablog.models import Experiment
        # this is a list of experiments, so get_object_or_404 will not work!
        experiment_list = Experiment.objects.filter(project__exact=project.id)
        
        # delete the project, notes, experiment & all events that come with it
        if 'deletebutton' in request.POST:
            note_list.delete()
            from lablog.models import Event
            for i in experiment_list:
                event_list = Event.objects.filter(experiment__exact=i.id)
                event_list.delete()
                # we can remove the call to this method, once the upstream bug 
                # has been fixed: http://code.djangoproject.com/ticket/6870
                remove_animal_list_link_from_experiment(i.id)
            
            experiment_list.delete()
            project.delete()            

        # return to project index
        return HttpResponseRedirect(reverse('index_project', args=(username, )))


# /project/slug/search/
def search(request, username, project_slug):

    # grab the project
    query_object = get_object_or_404(Project, author__username__exact=username, slug__exact=project_slug)

    # build the search terms
    terms = request.POST['terms']
    from lablog.utils.search import extract_words, build_query
    words = extract_words(terms)
    # search events
    query1 = build_query(words, ['text_field', ])
    # search notes
    query2 = build_query(words, ['occasion', 'entry'])    
    
    # get a list of all experiments, events and notes
    from lablog.models import Note, Event, Experiment
    experiments = Experiment.objects.filter(project = query_object.pk).order_by('-data', '-start_date')

    events = Event.objects.filter(query1, author__username__exact = username, experiment__in = experiments)
    notes = Note.objects.filter(query2, project = query_object.pk)
    nbr_results = events.__len__() + notes.__len__()

    return direct_to_template(request, 'project/search_results.html', {
        'nbr_results': nbr_results, 'search': words, 'events': events, 
        'notes': notes, 'project': query_object, }
    )



