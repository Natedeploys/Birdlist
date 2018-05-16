from django.views.generic.simple import direct_to_template

## show a default page for /lablog/collaboration/
def index(request, username):
    return direct_to_template(request, 'collaboration/collaboration-index.html')
