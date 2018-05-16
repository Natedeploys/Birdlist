# -*- coding: utf-8 -*-

"""
Low-level RememberTheMilk connection handling.

Heavily inspired by rtmapi, but modified to use JSON instead of
(frequently confusing) XML, add logging, and be explicit
"""

import hashlib
import httplib2
import urllib
import simplejson
import logging

__all__ = ('RtmException', 'RtmConnector')

logger = logging.getLogger(__name__)

class RtmException(Exception): pass
class RtmConnectException(RtmException): pass
class RtmServiceException(RtmException): pass

class RtmConnector(object):
    _auth_url = "http://api.rememberthemilk.com/services/auth/"
    _base_url = "http://api.rememberthemilk.com/services/rest/"
    
    """
    @param api_key: your API key
    @param shared_secret: your shared secret
    @param perms: desired access permissions, one of "read", "write"
                  and "delete"
    @param token: token for granted access (optional, if not set,
                  authentication must be performed later)
    """
    def __init__(self, api_key, shared_secret, perms = "read", token = None):
        self.api_key = api_key
        self.shared_secret = shared_secret
        self.perms = perms
        self.token = token
        self.user_id = self.user_name = self.user_full_name = None
        self.http = httplib2.Http()
    
    ######################################################################
    # Authentication (routines to call if token is not yet known)
    ######################################################################

    """
    Authenticate as a desktop application.
    
    @returns: (url, frob) tuple with url being the url the user should open and
                          frob the identifier for usage with retrieve_token
                          after the user authorized the application
    """
    def authenticate_desktop(self):
        rsp = self.call_anonymously("rtm.auth.getFrob")
        frob = rsp["frob"]
        url = self._make_request_url(
            called_url = self._auth_url, perms=self.perms, frob=frob)
        return url, frob
    
    """
    Authenticate as a web application.
    @returns: url
    """
    def authenticate_webapp(self):
        url = self._make_request_url(
            called_url = self._auth_url, perms=self.perms)
        return url
    
    """
    Checks whether the stored token is valid. Apart from testing that,
    on success sets user_id, user_name and user_full_name

    @returns: bool validity
    """
    def token_valid(self):
        if self.token is None:
            return False
        try:
            rsp = self.call_anonymously("rtm.auth.checkToken",
                                        auth_token=self.token)
            self._set_user_attributes(rsp['auth']['user'])
        except RtmServiceException, e:
            logger.info("Failure verifying token: %s" % str(e))
            return False
        return True
    
    """
    Retrieves a token for the given frob

    Additionally, on success sets .token, .user_id, .user_name .user_full_name attributes

    @returns: True/False
    """
    def retrieve_token(self, frob):
        try:
            rsp = self.call_anonymously(
                "rtm.auth.getToken", frob=frob)
        except RtmServiceException, e:
            logger.warn("Failure retrieving token: %s" % str(e))
            self.token = None
            self.user_id = self.user_name = self.user_full_name = None
            return False
        self.token = rsp['auth']['token']
        self._set_user_attributes(rsp['auth']['user'])
        return True

    ######################################################################
    # Main call routines
    ######################################################################
    
    def call_anonymously(self, method_name, **params):
        """
        Executes given method without authorization credentials.

        @param method_name called metod (for example "rtm.auth.checkToken"
               or "rtm.test.echo")
        @param params any extra params named according to docs (note: params with value
               None will be dropped)
        @result output structure without wrappers

        See http://www.rememberthemilk.com/services/api/methods/ for method list.
        """
        return self._make_request(method = method_name, **params)
    
    def call_authorized(self, method_name, **params):
        """
        Executes given method with authorization credentials.

        @param method_name called metod (for example "rtm.auth.checkToken"
               or "rtm.test.echo")
        @param params any extra params named according to docs (note: params with value
               None will be dropped)
        @result output structure without wrappers

        See http://www.rememberthemilk.com/services/api/methods/ for method list.
        """
        return self._make_request(method = method_name, auth_token = self.token, **params)

    call = call_authorized
    
    ######################################################################
    # Internal helpers
    ######################################################################

    def _make_request(self, method, called_url = None, **params):
        final_url = self._make_request_url(called_url = called_url, method=method, **params)
        logger.debug("Calling %s" % final_url)
        info, data = self.http.request(
            final_url,
            headers={'Cache-Control':'no-cache, max-age=0'})
        if info['status'] != '200':
            raise RtmConnectException("Connection failure: %s (%s)" % (
                    info['status'], info.get('reason', '')))
        logger.debug("Call to %s executed. Result: %s" % (method, data))
        reply = simplejson.loads(data)
        rsp = reply['rsp']
        if rsp['stat'] != "ok":
            err = rsp.get("err")
            if err:
                raise RtmServiceException(
                    "Service failure: %(code)s (%(msg)s)" % err)
            else:
                raise RtmServiceException(
                    "Unknown service failure during call to %s" % final_url)
        return rsp
    
    def _make_request_url(self, called_url = None, **params):
        """
        Construct final REST-style URL. Adds format, api_key and signature.
        """
        params["api_key"] = self.api_key
        params["format"] = "json"
        param_pairs = [ (k,RtmConnector._to_unicode(v))
                              for k,v in params.iteritems()
                              if v is not None ]
        param_pairs.append( ("api_sig", self._sign_request(param_pairs)) )
        quote_utf8 = lambda s: urllib.quote_plus(s.encode('utf-8'))
        params_joined = "&".join("%s=%s" % (quote_utf8(k), quote_utf8(v))
                                           for k, v in param_pairs)
        return (called_url or self._base_url) + "?" + params_joined
    
    def _sign_request(self, param_pairs):
        param_pairs.sort()
        request_string = self.shared_secret + u''.join(k+v
                                                       for k, v in param_pairs)
        return hashlib.md5(request_string.encode('utf-8')).hexdigest()

    def _set_user_attributes(self, user):
        self.user_id = user['id']
        self.user_name = user['username']
        self.user_full_name = user['fullname']

    @staticmethod
    def _to_unicode(txt):
        if type(txt) is unicode:
            return txt
        return txt.decode("utf-8")
