'''
when the birds in a given cage are registered completely we can verify the
content of that given cage.

here we provide functions that enable batch processing of registered birds.
'''

import datetime
from birdlist.models import Bird, Cage


# set these paths to read the correct files

DJANGO_PATH = '/home/michael/code/songbird-django/code/'
#DJANGO_PATH = '/home/db/django/'
DATA_PATH = 'django_projects/internal_applications/birdlist/db_batch_operations/data/'
CENSUS_FILE = '20110623_census.txt'



def read_batch_file(batch_file):
    '''
    readin in a file that follows the syntax of the files given in the modules
    subfolder data
    '''

    readlist = []
    fid = open(batch_file, 'r')

    for line in fid.readlines():
        
        # only read lines starting with ==
        if not line[:2] == '==':
            continue
        # the lines are separated with ==
        splits = line.rsplit('==')

        # exclude example cage
        if splits[1] == 'cage name':
            continue
        
        # register the date
        if splits[1] == 'date':
            year = int(splits[2].rsplit('-')[0])
            month = int(splits[2].rsplit('-')[1])
            day = int(splits[2].rsplit('-')[2])

            date = datetime.datetime(year, month, day)

        # a text that can be added to the comment field of the birds
        elif splits[1] == 'text':
            text = splits[2].rstrip()

        # otherwise it has to be cage related bird info
        else:
            # parse the cages
            c = {}
            c['cage'] = Cage.objects.get(name=splits[1])
            c['birds'] = []

            for birdname in splits[2].rsplit(','):
                c['birds'].append(Bird.objects.get(name=birdname.rstrip()))
            
            readlist.append(c)

    fid.close()

    return date, text, readlist


def process_missing_birds(date, text, readlist, save=False):
    '''
    '''
    for c in readlist:
        for b in c['birds']:
            if b.comment:
                b.comment = b.comment + '\n\n' + text
            else:
                b.comment = text

            if not b.missing_since:
                b.missing_since = date

            print 
            print b.name
            print b.missing_since
            print b.comment
            
            if save:
                b.save()


def do_census_db_mutations():
    '''
    main function to be executed
    '''
    d, t, r = read_batch_file(DJANGO_PATH+DATA_PATH+CENSUS_FILE)
    process_missing_birds(d,t,r, save=True)

    print
    print 'done! '
