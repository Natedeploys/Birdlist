from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from lablog.views.basic.lablog_main import not_implemented, server_error

from RememberTheMilk.RtmApiLib import *

import logging
logger = logging.getLogger(__name__)

api_key = 'b489cadc229bf9e61f2be487a042785f'
shared_secret = '578db24aac96f4dd'
APP_NAME = "Lablog"
TOKEN_LABEL = "default-user-token"

# /lablog/user/rtm/
def index(request, username):
    # check if keyring item exist
    # if true  -> send to browse
    # if false -> send to auth.
    try:
        ''' importing these modules might fail '''
        from mekk.rtm.connect import create_and_authorize_connector
        from mekk.rtm import RtmClient, RtmConnector
        connector = create_connector(APP_NAME, api_key, shared_secret)
        if not connector.token_valid():
            return HttpResponseRedirect(reverse('rtm_auth', args=(username, )))
        else:
            return HttpResponseRedirect(reverse('rtm_browse', args=(username, )))
    except Exception, e:
        logger.info("error in index: %s" % str(e))
        return server_error(request)


# /lablog/user/rtm/auth/
def authenticate(request, username, frob = None):
    # send to auth url in frame
    # wait until user presses confirm button.
    try:
        message = ''
        if request.method == 'POST':
            if request.POST.has_key('frob'):
                frob = request.POST['frob']
                connector = create_connector(APP_NAME, api_key, shared_secret)
                if connector.retrieve_token(frob):
                    import keyring
                    # throws error if neither OSXKeychain, KDEKWallet or GnomeKeyring
                    # are installed. Will need to switch to different backend for 
                    # webserver
                    # error in authenticate: [Errno 13] Permission denied: '/var/www/keyring_pass.cfg'
                    keyring.set_password(APP_NAME, TOKEN_LABEL, connector.token)
                    return HttpResponseRedirect(reverse('rtm_browse', args=(username, )))
                else:
                    message = "Authentication failed. Please try again!"

        connector = create_connector(APP_NAME, api_key, shared_secret)
        url, frob = connector.authenticate_desktop()
        return direct_to_template(request, 'rtm/auth.html', 
                                {'url': url, 'frob': frob, 'message': message, })
        
    except Exception, e:
        logger.info("error in authenticate: %s" % str(e))
        return server_error(request)


# /lablog/user/rtm/browse/
def browse(request, username):
    try:
        ''' importing these modules might fail '''
        from mekk.rtm.connect import create_and_authorize_connector
        from mekk.rtm import RtmClient, RtmConnector
        connector = create_connector(APP_NAME, api_key, shared_secret)
        if not connector.token_valid():
            return HttpResponseRedirect(reverse('rtm_auth', args=(username, )))

        # everything is ok - show the content            
        client = RtmClient(connector)
        test_list = client.find_or_create_list(u"Work")
        work_items = list(client.find_tasks(list_id = test_list.id))
        tasksByTag = ''
        return direct_to_template(request, 'rtm/index.html', 
	        {'tasksByTag': tasksByTag, 'client': client, 'work_items': work_items, })

    except Exception, e:
        logger.info("error in browse: %s" % str(e))
        print e
        return server_error(request)


def create_connector(app_name, api_key, shared_secret, permission = "delete"):
    try:
        import keyring
        from mekk.rtm.rtm_connector import RtmConnector

        token = keyring.get_password(app_name, TOKEN_LABEL)
        connector = RtmConnector(api_key, shared_secret, permission, token)
        
        return connector

    except Exception, e:
        logger.info("error in create_connector: %s" % str(e))
        print e
        return server_error(request)        


''' original create_and_authorize_connector
def create_and_authorize_connector(app_name, api_key, shared_secret, permission = "delete"):
    try:
        import keyring
        from mekk.rtm.rtm_connector import RtmConnector
        TOKEN_LABEL = "default-user-token"
        token = keyring.get_password(app_name, TOKEN_LABEL)
        connector = RtmConnector(api_key, shared_secret, permission, token)
        
        if not connector.token_valid():
            url, frob = connector.authenticate_desktop()
            webbrowser.open(url)
            
            
            wait_for_authorization()
            if connector.retrieve_token(frob):
                keyring.set_password(app_name, TOKEN_LABEL, connector.token)
                print "Access token saved"
            else:
                raise RtmServiceException("Failed to grab access token")

        return connector
    except Exception, e:
        print e
        return server_error(request)
'''		
		  	
