from django.conf import settings

# Don't forget to add these context processors to the settings.py file if you 
# want to use them.

def base_url(request):
    return {'base_url': settings.BASE_URL}
# EOF
