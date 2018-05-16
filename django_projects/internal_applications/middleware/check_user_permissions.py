from django.views.generic.simple import direct_to_template

class UserOwnsDirectoryMiddleware(object):

    """

    This middleware makes sure that users don't try to look at other users' data

    """

    def process_view(self, request, view_func, view_args, view_kwargs):

        assert hasattr(request, 'user'), """Make sure that the authentication\
                middleware and template context processors\
                are loaded in the settings.py file."""

        # are any keyword arguments supplied?    
        if len(view_kwargs):

            # extract the keys
            keys = view_kwargs.keys()
            for kw in keys:
                if kw == "username":
                    # make sure that the user directory matches, or that user is 
                    # a superuser
                    if (view_kwargs[kw] == request.user.username) or request.user.is_superuser:
                        return None
                    else:
                        return direct_to_template(request,'lablog/basic/access_error.html')


