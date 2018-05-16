'''
functions to process birds that are given away ..

'''

from birdlist.db_batch_operations.census import read_batch_file
from birdlist.utils.bird import do_checkout_from_database

from birdlist.models import Cage, Bird
from django.contrib.auth.models import User


# set these paths to read the correct files

DJANGO_PATH = '/home/michael/code/songbird-django/code/'
#DJANGO_PATH = '/home/db/django/'
DATA_PATH = 'django_projects/internal_applications/birdlist/db_batch_operations/data/'
GIVEAWAY_FILE = '20110623_giveaway.txt'



def process_birds_given_away(date, text, readlist):
    '''
    '''
    hob = User.objects.get(username='hob')

    # go through all cages
    for c in readlist:
        # do it for all birds
        for b in c['birds']:

            print 
            print b.name

            # add a comment to the birds
            if b.comment:
                b.comment = b.comment + '\n\n' + text
            else:
                b.comment = text
           
            print b.comment

            # check the bird out of the database
            do_checkout_from_database(b, date, Bird.EXIT_GIVENAWAY, hob)


def do_giveaway_db_mutations():
    '''
    main function to be executed
    '''
    d, t, r = read_batch_file(DJANGO_PATH+DATA_PATH+GIVEAWAY_FILE)
    process_birds_given_away(d,t,r)

    print
    print 'done! '
