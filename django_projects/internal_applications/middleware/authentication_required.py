from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from re import compile


class AuthenticationRequiredMiddleware(object):

    """
    This middleware requires a user to be authenticated to view any page other
    than LOGIN_URL or any URL listed in LOGIN_NOAUTH_URLS. 

    """


    def __init__(self):

        """ no authentication is needed for the login url """
        NOAUTH_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]

        """ append all the other urls from the LOGIN_NOAUTH_URLS variable set in the 
            settings file """
        if hasattr(settings, 'LOGIN_NOAUTH_URLS'):
            NOAUTH_URLS += [compile(url) for url in settings.LOGIN_NOAUTH_URLS]

        self.noauth = NOAUTH_URLS


        """ which URL require an authentication ? """
        REQUIREAUTH_URLS = []
        if hasattr(settings, 'LOGIN_REQUIREAUTH_URLS'):
            REQUIREAUTH_URLS += [compile(url) for url in settings.LOGIN_REQUIREAUTH_URLS]

        self.requireauth = REQUIREAUTH_URLS



    def process_view(self, request, view_func, view_args, view_kwargs):
    
        assert hasattr(request, 'user'), """Make sure that the authentication\
                middleware and template context processors\
                are loaded in the settings.py file. Also check that MYSQL is running."""
                

        if not request.user.is_authenticated():
            """ extract URL user requested """
            requested_url = request.path.lstrip('/')

            """ show the page right away if this is a non authentication 
                required page """
            if any(url.match(requested_url) for url in self.noauth):
                return None

            """ check if this URL matches any of the above defined URLs """
            if not any(url.match(requested_url) for url in self.requireauth):
                """ no URL matched, so wrap the login decorator around it """
                return login_required(view_func)(request, *view_args, **view_kwargs)

