from lablog.views.basic.lablog_main import not_implemented, server_error
from django.views.generic.simple import direct_to_template

# /lablog/user/external_view/
def index(request, username):
	return not_implemented(request, "index")
	
