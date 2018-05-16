#
#
#

from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER,\
        CAGE_HISTORY_FILE, EXP_HISTORY_FILE, USERS

from birdlist.models import Activity, Activity_Type, Bird
from django.contrib.auth.models import User

from birdlist.dbconversion.birds import convert_date

import time, datetime, csv


def generate_activities(debug=0):

    # get rid of old stuff
    delete_old_entries(debug=debug)
    # first we'll need the actity types to be populated
    create_activity_types(debug=debug)
    # we need a complete list of users to assign the activities originator correctly
    #create_users(debug=debug)
    # finally
    readin_activities(debug=debug)

    print 'all done'


def delete_old_entries(debug=0):

    # kill all data by truncating table
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_activity`')
    cursor.execute('TRUNCATE TABLE `birdlist_activity_type`')
    cursor.close()
    connection.close()

    print 'deleted old entries'


def create_activity_types(debug=0):
    '''
    '''
    activity_types = [
            ('Experiment', '', True, '2005-01-01'),
            ('Cage Transfer', '', True, '2005-01-01'),
            ('Health Status', '', True, '2010-09-01'),
            ]

    for at in activity_types:
        dat = Activity_Type(name=at[0], description=at[1], in_use=at[2], creation_date=at[3])
        dat.save()

    print 'activity types created'


def add_users(debug=0):
    '''
    '''
    for user in USERS:
        if User.objects.filter(username=user[0]).__len__()<1:
            new_user = User(username=user[0], first_name=user[1], last_name=user[2],\
                    email=user[3], password='password', is_staff=user[4])
            new_user.save()

    print 'users added'


def readin_activities(debug=0):
    '''
    since we will merge two tables of the old access database (cage history, experiment history)
    into the new activities table we will first construct a list of all future entries, sort them
    according to start_date and then save them one after the other to preserve order.
    '''

    activity_list = []
    
    # read the experiment history file first
    csvfile = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + EXP_HISTORY_FILE)
    fileReader = csv.reader(csvfile, delimiter = DELIMITER, quotechar = '"')
    AType = Activity_Type.objects.get(name='Experiment')

    for exp in fileReader:
        try:
            django_bird = Bird.objects.get(name=exp[1])
        except:
            print 'could not find bird %s in database -> id: %s' % (exp[1], exp[0])
            continue
        user = get_django_user(exp[8])
        concatenated_activity_content = exp[2] + '\n----------------------------------------\n' + exp[10].decode("cp1252")
        if exp[3]:
            activity_list.append(
                    Activity(bird=django_bird, originator=user, start_date=convert_date(exp[3]),\
                            end_date=convert_date(exp[4]), activity_type=AType, severity_grade=int(exp[9]),\
                            activity_content=concatenated_activity_content
                            )
                    )
        else:
            print 'no start date for experiment No %s' % exp[0]
            continue

    csvfile.close()
    
    # read the cage history file first
    csvfile = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + CAGE_HISTORY_FILE)
    fileReader = csv.reader(csvfile, delimiter = DELIMITER, quotechar = '"')
    AType = Activity_Type.objects.get(name='Cage Transfer')

    for transfer in fileReader:
        try:
            django_bird = Bird.objects.get(name=transfer[1])
        except:
            print 'could not find bird %s in database' % transfer[1]
            continue
        user = get_django_user(transfer[4])
        concatenated_activity_content = 'old db transfer: moved out of cage %s' % transfer[2]
        if transfer[3]:
            activity_list.append(
                    Activity(bird=django_bird, originator=user, start_date=convert_date(transfer[3]),\
                            end_date=convert_date(transfer[3]), activity_type=AType, severity_grade=0,\
                            activity_content=concatenated_activity_content
                            )
                    )
        else:
            print 'no start date for cage transfer No %s' % transfer[0]
            continue

    csvfile.close()

    # now sort all these activities according to start_date
    activity_list.sort(key=lambda x: datetime.date(date_to_ints(x.start_date)[0],\
            date_to_ints(x.start_date)[1], date_to_ints(x.start_date)[2]).toordinal(), reverse=False)

    # safe all the activities
    for acty in activity_list:
        acty.save()

    print 'done importing activities!!'

    return 




# H E L P E R   F U N C T I O N S
# -----------------------------------------------------------------------------------------------

def date_to_ints(isostring):
    '''
    'YYYY-MM-DD' -> YYYY, MM, DD
    '''
    try:
        a, b, c = isostring.split('-')
        return int(a), int(b), int(c)
    except:
        print 'FUUUUUUCK'
        return 2000, 01, 01


def get_django_user(name_string):
    '''
    '''
    name_string_orig = name_string
    from os import linesep
    # remove newlines
    name_string = name_string.rstrip(linesep)
    # remove spaces
    name_string = name_string.rstrip()
    # lowercase
    name_string = name_string.lower()
    for user in USERS:
        if name_string in user[5]:
            try:
                return User.objects.get(username=user[0])
            except:
                print 'cannot find user object with username: %s' % user[0]
    # else
    print 'cannot find user: %s' % name_string
    print 'orig string was: %s' % name_string_orig
    return User.objects.get(username='unknown')


def read_list_of_users(debug=0):
    '''
    this is a helper function to find the list of users having been active in the db
    we will have to scan the Cage History and the Experiment History files
    '''
    
    users_list = [] 

    # read the experiment history file first
    csvfile = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + EXP_HISTORY_FILE)
    fileReader = csv.reader(csvfile, delimiter = DELIMITER, quotechar = '"')

    for exp in fileReader:
        users_list.append(exp[8])

    csvfile.close()

    # now read the cage history file
    csvfile = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + CAGE_HISTORY_FILE)
    fileReader = csv.reader(csvfile, delimiter = DELIMITER, quotechar = '"')

    for exp in fileReader:
        users_list.append(str(exp[4]))

    csvfile.close()

    return list(set(users_list))
