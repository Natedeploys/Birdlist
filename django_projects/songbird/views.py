from django.http import HttpResponse
from django.shortcuts import redirect

def start(request):
    return redirect('index_birdlist')
    #return HttpResponse("We are still in alpha phase. Please come back and visit us later.")

def keep_alive(request):
    return HttpResponse("OK")

def nothing(request):
    response = HttpResponse()
    response.status_code = 204
    return response

def auto_logout(request):
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    logout(request)
    go_to = request.GET.get('next')
    return HttpResponseRedirect(go_to)
    
### server errors    
""" taken from http://projects.via-kitchen.com/picolog/browser/trunk/common/views.py """	
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
def generic_page_not_found(request, main_page=None):
    """
	    Handling error 404.
    """
    
    if not main_page:
        main_page = reverse('songbird.views.start')
    
    referer = request.META.get('HTTP_REFERER')
    if not referer or referer == main_page:
        referer = None
        
    description = _(u"The requested URL %(path)s was not found.") % {'path': request.path}
    c = RequestContext(request, {
        'description': description,
        'referer': referer,
        'title': _(u"Not found"),
        'main_page': main_page,
    })
    
    t = loader.get_template('lablog/basic/error.html')
    return HttpResponse(t.render(c), status=404)


def generic_server_error(request, main_page=None):
    """
    Handling Error 500.                                                                  
    """
    if not main_page:
        main_page = reverse('songbird.views.start')
    
    referer = request.META.get('HTTP_REFERER')
    if not referer or referer == main_page:
        referer = None
    
    c = RequestContext(request, {
        'description': _(u"The server encountered an internal server error."),        
        'referer': referer,                                
        'title': _(u"Internal server error"),
        'main_page': main_page,
    })
    
    t = loader.get_template('lablog/basic/error.html')
    return HttpResponse(t.render(c), status=500)


def generic_not_implemented(request, custom_section_id, main_page=None):
    """
    Handling unavailable content                                                               
    """
    
    if not main_page:
        main_page = reverse('songbird.views.start')
        
    referer = request.META.get('HTTP_REFERER')
    if not referer or referer == main_page:
        referer = None
    
    c = RequestContext(request, {
        'description': _(u"The function you requested is not available yet."),        
        'referer': referer,                                
        'title': _(u"Function not available"),
        'section_id': custom_section_id or "homepage",
        'main_page': main_page,
    })
    
    t = loader.get_template('lablog/basic/error.html')
    return HttpResponse(t.render(c), status=200)    
    

################################################################################
# pop-up addon
# see http://www.hoboes.com/Mimsy/?ART=675

from django.utils.html import escape
from django.views.generic.simple import direct_to_template
from lablog.utils.generic import copy_data_from_request_set_author

def handlePopAdd(request, addForm, model = 'lablog', field = None, username = None):

    if request.method == "POST":

        new_data = copy_data_from_request_set_author(request, username)
        form = addForm(username, new_data)

        if form.is_valid():
            try:
                newObject = form.save()
            except forms.ValidationError, error:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(newObject._get_pk_val()), escape(newObject)))

    else:
        form = addForm(username)

    pageContext = {'form': form, 'field': field, 'add': True, 'change': False, 'username': username, }

    if model == 'lablog':
        return direct_to_template(request, 'basic/popup-lablog.html', pageContext)
    elif model == 'birdlist':
        return direct_to_template(request, 'basic/popup-birdlist.html', pageContext)


from django.shortcuts import get_object_or_404        
def handlePopEdit(request, editForm, editObject, username, field, item_id):

    query_list = get_object_or_404(editObject, author__username__exact=username, id__exact=item_id)

    if request.method == "POST":
        form = editForm(username, request.POST, instance=query_list)
        
        if form.is_valid():
                try:
                    newObject = form.save()
                except forms.ValidationError, error:
                    newObject = None
                if newObject:
                    return HttpResponse('<script type="text/javascript">window.close()</script>')
    else:
        form = editForm(username, instance=query_list)

    pageContext = {'form': form, 'field': field, 'add': False, 'change': True, 'item_id': item_id, 'username': username, }
    return direct_to_template(request, 'basic/popup-lablog.html', pageContext)        


