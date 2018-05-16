from django.template import Library
register = Library()

from django.template.defaultfilters import cut

def returnStringBasedOnBoolean(strings, booleanvalue):

    "Removes all | separators, and returns the first or the second entry"

    separator = '|'
    subvalue = strings.split(separator)

    return_var = ''

    if booleanvalue == 0:
        return_var = subvalue[0]
    else:
        'in case there is only one color given, use it'
        if subvalue.__len__() == 2:
            return_var = subvalue[1]
        else:
            return_var = subvalue[0]

    return return_var

register.filter('returnStringBasedOnBoolean', returnStringBasedOnBoolean)
