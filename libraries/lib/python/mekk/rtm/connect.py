# -*- coding: utf-8 -*-

"""
Routines which make it easier to connect application in 
console application/script case and some desktop cases. 
"""

import webbrowser
import keyring
from rtm_connector import RtmConnector, RtmException, RtmServiceException
import getpass

def _console_invite_to_auth(): 
    print "Use the page just opened in the browser to let me access your RememberTheMilk account"

def _console_wait_for_user():
    raw_input("Press Enter once you finished browser authentication")

def create_and_authorize_connector(
    app_name, api_key, shared_secret,
    permission = "delete",
    invite_to_authorize = _console_invite_to_auth,
    wait_for_authorization = _console_wait_for_user):
    """
    Creates and returns RtmConnector object. Ensures it contains
    valid access token (if not, performs browser-based authorization).
    Grabbed token (if any) is saved in keyring for future use (using app_name
    to distnguish usage cases)
    """
    TOKEN_LABEL = "default-user-token"

    token = keyring.get_password(app_name, TOKEN_LABEL)

    connector = RtmConnector(api_key, shared_secret, permission, token)
    
    if not connector.token_valid():
        url, frob = connector.authenticate_desktop()
        invite_to_authorize()
        webbrowser.open(url)
        wait_for_authorization()
        if connector.retrieve_token(frob):
            keyring.set_password(app_name, TOKEN_LABEL, connector.token)
            print "Access token saved"
        else:
            raise RtmServiceException("Failed to grab access token")

    return connector

def _prompt_secure_data(what):
    return getpass.getpass("Enter %s: " % what)

def create_and_authorize_connector_prompting_for_api_key(
    app_name,
    permission = "delete",
    invite_to_authorize = _console_invite_to_auth,
    wait_for_authorization = _console_wait_for_user,
    prompt_secure_data = _prompt_secure_data):
    """
    Creates and authorizes connector interactively asing
    for api key (and saving it for future uses)
    """
    API_LABEL = "api-key"
    SEC_LABEL = "sec-code"

    api_key = keyring.get_password(app_name, API_LABEL)
    if not api_key:
        api_key = prompt_secure_data("API Key")
        keyring.set_password(app_name, API_LABEL, api_key)

    api_sec = keyring.get_password(app_name, SEC_LABEL)
    if not api_sec:
        api_sec = prompt_secure_data("shared secret")
        keyring.set_password(app_name, SEC_LABEL, api_sec)

    try:
        connector = create_and_authorize_connector(app_name, api_key, api_sec)
        return connector
    except RtmServiceException, e:
        if "Invalid API Key" in str(e):
            keyring.set_password(app_name, API_LABEL, "")
        if "Invalid signature" in str(e):
            keyring.set_password(app_name, SEC_LABEL, "")
        raise

