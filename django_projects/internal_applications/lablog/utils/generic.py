''' generic helper functions '''
    
def get_user_object(username):

    # create the correct user object for the current user
    from django.contrib.auth.models import User
    
    user_object = User.objects.get(username = username)
    return user_object
    
def copy_data_from_request_set_author(request, username = None):
    
    # copy the post values so we can change them
    new_data = request.POST.copy()
    
    if username == None:
        return new_data

    # set the author field to the user id of the username in the url
    # this way an admin can create experiment for other users.
    user_object = get_user_object(username)
    new_data['author'] = user_object.id
    
    return new_data


def convert_date_time_to_seconds_since_epoch(this_date, this_time):
    ' converts the given date & time to seconds since epoch '

    from datetime import datetime
    import time
    secs_since_epoch = int(time.mktime(datetime.combine(this_date, this_time).utctimetuple()))

    return secs_since_epoch 


def order_and_sort(request, default='asc'):
    ## START allow user to order results
    
    # order by what field? - not implemented yet
    # import re
    #order_by = re.match(r"(?:date|time|name)$", request.GET['order_by'])
    order_by = ''
    
    sort_dir = default
    order = '-'
    if request.GET.__contains__('sort'):
        sort_dir = request.GET['sort']
    
    if sort_dir == 'desc':
        order = ''

    ## END allow user to order results
    return order, sort_dir


''' tagging '''
from tagging.utils import edit_string_for_tags
def sync_tags_with_object(Tag, query_object):

    # add_tag() doesn't sync the field of the event model
    # see bug: http://code.google.com/p/django-tagging/issues/detail?id=235
    # therefore we manually retrieve the tags and set them explicitly again.
    tags = Tag.objects.get_for_object(query_object)
    new_tags = edit_string_for_tags(tags)
    query_object.tags = new_tags

    # the save method will change the tags in the Tag model!
    query_object.save()


def tag_object(query_object, string):
    # tag query_object with 'string'
    from tagging.models import Tag
    tags = Tag.objects.get_for_object(query_object)
    nbr_tags = len(tags)
    # hack for stupif tagging bug, where the first multi-word tag always 
    # get's split up into multiple tags.
    if nbr_tags == 0:
        query_object.tags = string
        query_object.save()
    else:
        str_tag0 = str(tags[0])
        # check if there is one existing tag only and whether the new 'string' 
        # has the same value as the one existing tag 'str_tag0'. 'string' might
        # also contain quotes ('"string"'), so I also check the 'string' without
        # the first and last character. If we don't do this check, then a 
        # multi word tag might be split up into two words again (as above).
        if not ((nbr_tags == 1) and ((str_tag0 == string) or (str_tag0 == string[1:-1]))):
            Tag.objects.add_tag(query_object, string)
            sync_tags_with_object(Tag, query_object)



