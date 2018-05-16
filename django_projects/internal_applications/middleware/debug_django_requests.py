from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from re import compile
from sys import modules


class DebugDjangoRequests(object):

    """
    This middleware requires a user to be authenticated to view any page other
    than LOGIN_URL or any URL listed in LOGIN_NOAUTH_URLS. 

    Make sure that the authentication middleware and template context processors
    are loaded in the settings.py file.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
    
        import logging
        """
        logging.debug(request.path)
        logging.debug(len(view_args))
        

        module = modules[view_func.__module__]
        logging.debug(dir(module))
        
        """
        if request.FILES:
            logging.debug(dir(request.FILES['file'].read))

        """
        root_urlconf = __import__(settings.ROOT_URLCONF)
        logging.debug(root_urlconf)
                
        for url in root_urlconf.urls.urlpatterns:
            logging.debug(url.__dict__.items.__name__)


        if len(view_args):
            logging.debug(view_args[0])
        """ 
        
        """ CAREFUL! not every view function has a func_name. 
        logging.debug(view_func.func_name)
        
        """
        
        if len(view_kwargs):
            for y in view_kwargs:
                # this is one dictionary element. need to get it's name & value
                logging.debug(y)

        
        for y in view_args:
            logging.debug(y)


