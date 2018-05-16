from django.conf import settings

# Don't forget to add these context processors to the settings.py file if you 
# want to use them.

def login_url(request):
    return {'login_url': settings.LOGIN_URL_LABLOG}

def logout_url(request):
    return {'logout_url': settings.LOGOUT_URL_LABLOG}

def admin_media_url(request):
    return {'admin_media_url': settings.ADMIN_MEDIA_PREFIX}

def lablog_media_url(request):
    return {'lablog_media_url': settings.LABLOG_MEDIA_URL}

# EOF
