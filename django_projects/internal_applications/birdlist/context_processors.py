from django.conf import settings

# Don't forget to add these context processors to the settings.py file if you 
# want to use them.

def birdlist_login_url(request):
    return {'birdlist_login_url': settings.LOGIN_URL_BIRDLIST}

def birdlist_logout_url(request):
    return {'birdlist_logout_url': settings.LOGOUT_URL_BIRDLIST}

# EOF
