import re
from django.db.models import Q

# modified from 
# http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap

def extract_words(query):
    # extract single words from query
    
    subentries = re.compile(r'"([^"]+)"|(\S+)').findall(query)
    cleanfunc = re.compile(r'\s{2,}').sub
    
    words = [cleanfunc(' ', (q[0] or q[1]).strip()) for q in subentries]

    return words


def build_query(terms, search_fields):
    # builds complex Q query
    
    # entire query
    query = None 
    for term in terms:
        # query for given term in each field
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
            
    return query


