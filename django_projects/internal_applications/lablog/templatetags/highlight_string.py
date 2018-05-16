from django.template import Library
import re 
register = Library()

from django.template.defaultfilters import safe

# idea taken from: 
# http://www.saltycrane.com/blog/2007/10/using-pythons-finditer-to-highlight/

# Create list of colors that is long enough for an insane amount of search words.
# If this is still not enough, then I don't care if the server crashes.
COLOR = ['orange', 'red', 'blue', 'violet', 'green', 'silver', 'yellow', 'maroon'] * 100

def highlight_string(string, args): 

    text = string
    words = args
    ''' if more than 50 words match, then regex will die, because only 100 groups
        are supported.
     '''
    
    
    regex_string = None
    # build complex regexp expression
    # group all words with (), and distinguish between entire word and 
    # substring so that we can highlight those cases differently.
    for i in words:
        if regex_string == None:
            # look for entire word only
            #regex_string = '(\\b%s\\b)' %i
            # look for any substring
            regex_string = '(%s)' %i
        else:
            # look for entire word only
            regex_string = regex_string + '|(\\b%s\\b)' %i
            # look for any substring            
            regex_string = regex_string + '|(%s)' %i
    
    regex = re.compile(r"%s" %regex_string, re.I)

    # initialize variables
    i = 0
    m = None
    output = ""

    for m in regex.finditer(text):
        output += "".join([text[i:m.start()], 
            "<strong><span style=\"color:%s\">" % COLOR[m.lastindex-1], 
            text[m.start():m.end()], "</span></strong>"])
        i = m.end()

    if m == None:
        return text
    else:        
        return safe("".join([output, text[m.end():], ""]))

register.filter('highlight_string', highlight_string)

