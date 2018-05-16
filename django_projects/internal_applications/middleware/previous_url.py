
class PreviousUrl(object):

    """

    This middleware saves the previously visited url. However, it is impossible
    to distinguish between real url and urls that load img or any other objects.

    """

    def process_request(self, request):

        """ extract URL user requested """
        requested_url = request.get_full_path()

        """ set the previous url once we created a current url """
        """ do not use has_key: http://code.djangoproject.com/ticket/3952 """
        if "current_url" in request.session:
            request.session['previous_url'] = request.session['current_url']

        """ update current url with the new value """
        request.session['current_url'] = requested_url

