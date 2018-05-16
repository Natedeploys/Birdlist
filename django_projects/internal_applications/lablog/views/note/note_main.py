# modules used in most views
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template    
from django.shortcuts import get_object_or_404
from lablog.models import Note, Project
from lablog.utils.generic import get_user_object
from lablog.forms.lablogforms import NoteForm

## we don't have any note listings, redirect to project list of user
def index(request, username):

    return HttpResponseRedirect(reverse('index_project', args=(username,)))


## show details for note
def detail(request, username, note_id):

    query_object = get_object_or_404(Note, id__exact=note_id)
    project = get_object_or_404(Project, note__exact=note_id)

    return direct_to_template(request,'note/note_object_detail.html', {'selected_object': query_object, 'project': project})


## delete event
def delete(request, username, note_id):

    # check if user really wants to delete this event
    if request.method == 'GET':
        return direct_to_template(request, 'note/note_object_delete.html',)
    
    # look at user response
    if request.method == 'POST':
        
        query_object = get_object_or_404(Note, id__exact=note_id)
        project = get_object_or_404(Project, note__exact=note_id)
        
        # delete event because user requested this.
        if 'deletebutton' in request.POST:
            query_object.delete()

        # return to experiment
        return HttpResponseRedirect(reverse('detail_project', args=(username, project.slug,)))
    

## edit selected note
def edit_form(request, username, note_id):

    query_list = get_object_or_404(Note, author__username__exact=username, id__exact=note_id)
    project = get_object_or_404(Project, note__exact=note_id)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = NoteForm(username, request.POST, instance=query_list)
        # generate form creating new object
        elif 'newbutton' in request.POST:
            form = NoteForm(username, request.POST)
        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_note', args=(username, query_list.id,)))
        
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
            return HttpResponseRedirect(reverse('detail_project', args=(username, project.slug,)))
                
    # Form has been called - user can fill it out.
    else:
        form = NoteForm(username, instance=query_list)

    return direct_to_template(request, 'note/forms/base_note_form.html', {
        'form': form, 'project': project, 'add': False, 'change': True, 'form_object_name': 'note'}
    )


## create new event - basically the same as edit_form
def new(request, username, project_id=None):

    project = ''
    if project_id is not None:
        project = get_object_or_404(Project, id__exact=project_id)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form creating new object
        if 'newbutton' in request.POST:
            form = NoteForm(username, request.POST)
        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_project', args=(username, project.slug,)))
        
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
                if project_id:
                    form_instance.project = project
                
            # save the instance    
            form_instance.save()
            
            # Redirect after POST
            if project_id:
                return HttpResponseRedirect(reverse('detail_project', args=(username, project.slug,)))
            else:
                return HttpResponseRedirect(reverse('index_project', args=(username, )))                
                
                
    # Form has been called - user can fill it out.
    else:
        form = NoteForm(username)

        if project_id is not None:
            # preselect the project field to the currently selected project
            project = Project.objects.get(id__exact=project_id)
            form.fields["project"].initial = project.id        
        
    return direct_to_template(request, 'note/forms/base_note_form.html', {
        'form': form, 'project': project, 'add': True, 'change': False, 'form_object_name': 'note'}
    )


## EOF
