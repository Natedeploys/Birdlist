from django.template import Library
register = Library()

from django.template.defaultfilters import cut, linebreaks, urlize

def grammar(value, arg):

    "Removes all | separators, creates line breaks and adds grammar description"

    separator = '|'
    subvalue = cut(value, separator)

    event_type_object = arg
    grammar_text = event_type_object.text_field.split(separator)
    grammar_text_len = grammar_text.__len__()

    # check whether a event type is given
    # also check whether user requested to not add grammar descriptions
    if (grammar_text[0] != "None") and (grammar_text[0] != "none") and (arg is not None):
        x = ''
        y = 0
        for i in subvalue.splitlines():
            if y < grammar_text_len:
                strg = ' ' + '(' + grammar_text[y] + ')'
            else:
                strg = ''

            x += i + strg + ' \r\n'
            y += 1

        subvalue = x

    value = urlize(subvalue)
    value = linebreaks(value)

    return value

register.filter('grammar', grammar)
