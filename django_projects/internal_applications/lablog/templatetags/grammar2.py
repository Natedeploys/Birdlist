from django.template import Library
register = Library()

from django.template.defaultfilters import cut, linebreaks, urlize

def grammar2(value, arg):

    "Removes all | separators, creates line breaks and adds grammar description"


    separator = '|'
    
    event_type_object = arg
    flag_text = event_type_object.flag_meaning.split(separator)
    flag_text_len = flag_text.__len__()

    return_var = ''

    if (flag_text[0] != "None") and (flag_text[0] != "none"):
        if value == 0:
            return_var += flag_text[0]
        else:
            return_var += flag_text[1]

    return return_var

register.filter('grammar2', grammar2)
