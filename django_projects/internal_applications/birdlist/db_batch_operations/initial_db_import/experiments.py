from birdlist.models import Couple, Coupling, Brood, CoupleLookup, Bird, Cage 
from coupling import find_bird_obj
from coupling import create_coupling

from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER,\
        BIRDLIST_FILE, COUPLING_FILE, BIRTHDAY_TOLERANCE

import time
today = time.strftime('%Y-%m-%d', time.gmtime())

# USERS with : username, email, first_name, last_name, staff status, possible names in access birdlist
users = (
        ('michael', 'Michael', 'Graber', 'michael@ini.phys.ethz.ch', True, ('michael', 'michi',)),
        ('kotowicz', 'Andreas', 'Kotowicz', 'kotowicz@ini.phys.ethz.ch', True, ('andreas', 'koto',)),
        ('rich', 'Richard', 'Hahnloser', 'rich@ini.phys.ethz.ch', True, ('rich', 'richard', 'richi',)),
        ('georg', 'Georg', 'Keller', 'georg@ini.phys.ethz.ch', True, ('georg', )), 
        ('katja', 'Katja', 'Naie', 'katja@ini.phys.ethz.ch', True, ('katja', )), 
        ('claude', 'Claude', 'Wang', 'cwang@ini.phys.ethz.ch', True, ('claude', )),
        ('josh', 'Joshua', 'Herbst', 'herbst@ini.phys.ethz.ch', True, ('josh', 'joshua', )),
        ('moritz', 'Moritz', 'Kirschmann', 'kirschi@ini.phys.ethz.ch', True, ('')),
        ('daniele', 'Daniele', 'Oberti', 'doberti@ini.phys.ethz.ch', True, ('daniele', 'doberti', )),
        ('aymeric', 'Aymeric', 'Nager', 'emri@ini.phys.ethz.ch', True, ('emri', 'aymeric', )),
        ('gokcen', 'Gokcen', 'Yildiz', 'gokcen123@gmail.com', True, ('gokcen', )),
        ('joergen', 'Joergen', 'Kornfeld', 'joergenk@ini.phys.ethz.ch', True, ('joergen', )),
        ('janie', 'Janie', 'Ondracek', 'janie@ini.phys.ethz.ch', True, ('janie', )),
        )


# GENERAL PROCEDURE
# -> populate ActivityTypes
# -> populate Users
# -> populate AnimalLicences



def populate_activity_types():
    '''
    '''

    # ACTIVITY TYPES WITH : name, description, in_use, creation_date
    activity_types = (
            ('Experiment', 'Any intervention we need a Licence for', True, today),
            ('Transfer', 'Moving a bird from one cage to another', True, today),
            ('State', 'Report about the state of a bird', True, today),
            )

    for act in activity_types:

        acty = Activity_Type(name=act[0], description=act[1], in_use[2], creation_date=act[3])
        acty.save

    print 'populated activity types'



def populate_users():
    '''
    '''


    


def generate_broods(debug=0):
    '''
    '''

    delete_old_entries(debug=debug)
    # I am using a different approach than Andreas
    #lookup = create_lookup_couple_juvenile();
    #create_new_brood_entries(lookup);
    stats_birthday_after_coupling = assign_parents_couple(debug=debug)

    print 'all done'

    return stats_birthday_after_coupling



def delete_old_entries(debug=0):
    '''
    '''

    # kill all data
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_brood`')
    cursor.close()
    connection.close()

    print 'deleted old entries'


def assign_parents_couple(debug=0):
    '''
    go through all the birds in the birdlist import file

        -> find couple that are parents
            if None:
                save bird_id in list
        -> find coupling session
            ** diff(start_coupling, birthday)
            ** coupling_duration
        -> find brood via BIRTHDAY_TOLERANCE
            if None:
                -> create brood
        -> assign brood to bird
            -> increase uncertainty to max if necessary

    ** diff(brood_birthday, brood_birthday)

    check birds with no parents

    do stats

    '''

    # logging
    from birdlist.dbconversion.logger import logger
    lognotes = 'B R O O D - G E N E R A T I O N   L O G'
    log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation.log', log_notes=lognotes)
    lognotes = 'B R O O D - G E N E R A T I O N   E R R O R - L O G'
    ERROR_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation_ERROR.log', log_notes=lognotes)
    lognotes = 'B R O O D - G E N E R A T I O N   M I S S I N G   P A R E N T S - L O G'
    MISSING_PARENTS_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/brood_generation_MISSING_PARENTS.log', log_notes=lognotes)

    # statistic containers
    stats_birthday_after_coupling = []
    stats_intrabrood_birthday_diff = []

    # read and process database transfer csv-file
    import csv
    file = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE)
    fileReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')

    # an old breeding cage as default breeding cage if breeding cage cannot be assigned
    default_cage = Cage.objects.get(id = 50)

    # now loop through all rows/birds of source file
    for birdy in fileReader:
        
        # ignore the first row and any tweak birds and birds in ignored_birds
        ignored_birds = ('dummy', 'dummy2',)
        if birdy[0].__contains__('Birdname') or birdy[0].upper().__contains__('TWEAK') or birdy[0] in ignored_birds:
            print 'did not import and thus handle in this context bird: ' + birdy[0]
            continue

        # ordered list of csv row attributes
        import_list = ['name', 'species', 'sex', 'birthday', 'uncertainty', 'cage',\
                'father', 'mother', 'exit date', 'cause of exit', 'comment', 'reserved', ]

        # fill in bird-container
        bird = {}
        for i, item in enumerate(import_list):
            bird[item] = birdy[i]

        # ----------------------------
        if debug:
            import_message = '\n\n' + bird['name'] + '\n-----------------------------------\n'
            for item in bird:
                import_message = import_message + item + ': ' + str(bird[item]) + '\n'
            import_message = import_message + '-----------------------------------\n\n' \
            
            print import_message
        # ----------------------------

