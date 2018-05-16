from django.template import Library
import re 
register = Library()

def replace_str(string, args): 

    search  = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, string)

register.filter('replace_str', replace_str)
