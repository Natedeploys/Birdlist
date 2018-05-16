"""
Tightens up response content by removed superflous line breaks and whitespace.

orgininally:
http://code.djangoproject.com/wiki/StripWhitespaceMiddleware

modified to reflect js / css problems:
http://justcramer.com/2008/12/01/spaceless-html-in-django/

(this was the problem: sometimes problem with the css - I don't know why
and it's not a consistent behaviour. the problem only occurs with google
chrome - very strange.)

see http://code.djangoproject.com/ticket/2594 for official solution (maybe someday)

"""

import re
class StripWhitespaceMiddleware:
    """
    Strips leading and trailing whitespace from response content.
    """
    def __init__( self ):
        self.whitespace = re.compile('\s*\n+\s*') 

    def process_response( self, request, response ):
        if 'text/html' in response['Content-Type'].lower():
            new_content = self.whitespace.sub( '\n', response.content )
            response.content = new_content
            return response
        else:
            return response

