"""

 template tag used to highlight and link animal names & cage names.
 This implementation only needs two SQL lookups per rendered template 
 - independent of the number of items that call this templatetag!
 
 MAKE SURE YOU CALL 'cage_animal_to_link' on the raw text, because I don't remove
 any html tags (which can lead to problems, if a search term is the last word which
 is followed by a closing html tag).
 

"""

import re
import traceback
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from birdlist.models import Bird, Cage


def build_regexp_string(values, pre_pad = ''):
    ''' 
        Build complex regexp expression.
        Check for cases like 'A-O' and 'IS_6': (?!-)(?!_)
        You can supply an optional 'pre_pad' argument.
        
        BE CAREFUL! depending on the number of 'values' this might result in 
        a very long regex_string which will lead to errors like:
        "Caught OverflowError while rendering: regular expression code size limit exceeded"
        
    '''
    regex_string = None
    for i in values:
        if regex_string == None:
            # look for entire word only
            regex_string = '\\b%s%s(?!-)(?!_)\\b' %(pre_pad, i)
        else:
            # look for entire word only
            regex_string = regex_string + '|\\b%s%s(?!-)(?!_)\\b' %(pre_pad, i)

    # uncomment if you want to debug overflow errors.
    #print regex_string.__len__()
    return regex_string


def regexp_finder(matches, text, keywords, pre_pad, MATCH_TYPE):
    ''' 
        Alternative to "build_regexp_string"
        Splits up text into words first, in case of a match, we do the regex.
  
        This function will only work if 'text' contains no html tags, otherwise 
        split(' ') might return unwanted results, i.e: o13r3</p>
    '''
    
    words_to_find = list()
    for i in text.split(' '):
        if keywords.__contains__(i):
            words_to_find.append(i)

    regex_string = build_regexp_string(words_to_find, pre_pad)
    for match in re.finditer(r"%s" %regex_string, text):
        # save match and MATCH_TYPE
        matches.append([match, MATCH_TYPE])
                
    return matches


# ignore previous bird name, i.e.:
# "bird was renamed/ringed from JU5a to o13r16"
# I only want to highlight and link the second name, which is the current one.
PRE_PAD_BIRD = 'to '
PRE_PAD_BIRD_LEN = 3

PRE_PAD_CAGE = ''

# define 
MATCH_TYPE_CAGE = 0
MATCH_TYPE_BIRD = 1


# exclude 'OutOfColony' because people will keep clicking on it and will bring 
# down our little server.
cages = Cage.objects.all().values_list('name', flat = True).exclude(name = 'OutOfColony')

# Build dict of bird name and bird id. If multiple birds exist with the same name
# then the first entry will be overwritten, i.e. we will use the last bird that
# occurs with that name.
birds = Bird.objects.all().values_list('name', 'id')
bird_dict = dict(birds)

# list of bird names.
birds = bird_dict.keys()


# create regexp strings - not used anymore.
'''
regex_string_cages = build_regexp_string(cages)
regex_string_birds = build_regexp_string(birds, PRE_PAD_BIRD)
'''


class ReverseProxy:
    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        length = len(self.sequence)
        i = length
        while i > 0:
            i = i - 1
            yield self.sequence[i]


def cage_animal_to_link(text):

    if text == '':
        return text

    try:
        # uncomment if you want to profile the code
        #import time
        #tStart = time.time()

        # preallocate matches        
        matches = []
        
        # look for matching cage names first
        matches = regexp_finder(matches, text, cages, PRE_PAD_CAGE, MATCH_TYPE_CAGE)
        # look for matching bird names
        matches = regexp_finder(matches, text, birds, PRE_PAD_BIRD, MATCH_TYPE_BIRD)
        
        # old way - crashes sometimes because 'regex_string_cages' is too long.
        # However, it works with surrounding html tags.
        #for match in re.finditer(r"%s" %regex_string_cages, text):
        #    # save match and MATCH_TYPE
        #    matches.append([match, MATCH_TYPE_CAGE])

        # uncomment if you want to profile the code
        #t_in = time.time() - tStart
        #print t_in
        
        # return here if nothing found - saves me the call to 'mark_safe'
        if not matches:
            return text

        for entries in ReverseProxy(matches):
            # extract name
            match = entries[0]
            # extract type
            match_type = entries[1]
            start = match.start()
            end = match.end()
            name = text[start:end]
            # construct url depending on the match type.
            if match_type == MATCH_TYPE_CAGE:
                url = reverse('cage_overview', args=[name])
            else:
                # I'm looking for the true name, so I need to skip the
                # "PRE_PAD_BIRD" part.
                name = name[PRE_PAD_BIRD_LEN:]
                start = start + PRE_PAD_BIRD_LEN
                bird_id = bird_dict[name]
                url = reverse('bird_overview', args=[bird_id])
        
            # add the link to the text.
            text = "%s <a href='%s'>%s</a>%s" % (text[:start], url, name, text[end:])
        
        return mark_safe(text)

    except Exception, e:
        # in case of error, return normal text and print error to console
        print traceback.format_exc()
        return text


register = template.Library()
register.filter(cage_animal_to_link)


