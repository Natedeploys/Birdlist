from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from lablog.models import Protocol

from lablog.forms.lablogforms import ProtocolForm

## show all protocols
def index(request, username):
    latest_protocols = Protocol.objects.select_related().filter(author__username__exact=request.user)
    return direct_to_template(request, 'protocol/protocol_list.html', {'latest_protocol': latest_protocols})
    
## show details for protocol
def detail(request, username, protocol_slug):
    query_object = get_object_or_404(Protocol, author__username__exact=username, slug__exact=protocol_slug)

    from lablog.models import Experiment
    experiments = Experiment.objects.filter(protocol = query_object.pk).order_by('-start_date')[:10] 
       
    return direct_to_template(request, 'protocol/protocol_detail.html', {'selected_object': query_object, 'experiments': experiments})
    
    

## edit the selected protocol
def edit_form(request, username, protocol_slug):
    
    query_list = get_object_or_404(Protocol, author__username__exact=username, slug__exact=protocol_slug)
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'savebutton' in request.POST:
            form = ProtocolForm(username, request.POST, instance=query_list)
        # generate form creating new object
        elif 'newbutton' in request.POST:
            form = ProtocolForm(username, request.POST)
        # revert changes
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('detail_protocol', args=(username, query_list.slug,)))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            form.save()
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_protocol', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ProtocolForm(username, instance=query_list) # An unbound form

    return direct_to_template(request, 'protocol/forms/base_protocol_form.html', {
        'form': form, 'protocol': query_list, 'add': False, 'change': True, 'form_object_name': 'protocol'}
    )


## create new project
def new(request, username):
    
    # If the form has been submitted...
    if request.method == 'POST':
    
        # generate form using the old object
        if 'newbutton' in request.POST:

            from lablog.utils.generic import copy_data_from_request_set_author
            new_data = copy_data_from_request_set_author(request, username)
            form = ProtocolForm(username, new_data)
            
        # return to experiment index
        elif 'cancelbutton' in request.POST:
            return HttpResponseRedirect(reverse('index_protocol', args=(username, )))
        
        if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data

            form.save()
                        
            # Redirect after POST
            return HttpResponseRedirect(reverse('detail_protocol', args=(username, form.cleaned_data['slug'],)))
                
    # Form has been called - user can fill it out.
    else:
        form = ProtocolForm(username) # An unbound form

    return direct_to_template(request, 'protocol/forms/base_protocol_form.html', {
        'form': form, 'protocol': '', 'add': True, 'change': False, 'form_object_name': 'protocol'}
    )


## delete project
def delete(request, username, protocol_slug):

    # check if user really wants to delete this project
    if request.method == 'GET':
        return direct_to_template(request, 'protocol/protocol_object_delete.html',)
    
    # look at user response
    if request.method == 'POST':

        protocol = get_object_or_404(Protocol, slug__exact=protocol_slug)

        # delete the project, notes, experiment & all events that come with it
        if 'deletebutton' in request.POST:
            protocol.delete()            

        # return to project index
        return HttpResponseRedirect(reverse('index_protocol', args=(username, )))
            
