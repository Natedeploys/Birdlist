from django.views.generic.simple import direct_to_template
    
# /help/
def index(request):
    '''
    '''
    
    return direct_to_template(request, 'birdlist/help_index.html', )
