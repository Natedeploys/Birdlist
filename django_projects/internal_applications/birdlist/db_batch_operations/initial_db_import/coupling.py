# we use the old dbs coupling entries to create couples, couplelookup and coupling

from birdlist.models import CoupleLookup, Couple, Coupling
from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER, COUPLING_FILE


def import_couples(debug=0):
    '''
    '''

    delete_old_entries(debug=debug);
    create_new_entries(debug=debug);
    print 'all done'


def delete_old_entries(debug=0):
    '''
    '''

    # kill all data
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_coupling`')
    cursor.execute('TRUNCATE TABLE `birdlist_couplelookup`')
    cursor.execute('TRUNCATE TABLE `birdlist_couple`')
    cursor.close()
    connection.close()

    print 'deleted old entries'


def create_new_entries(debug=0):
    '''
    '''

    # file preparation
    import csv
    from birdlist.dbconversion.birds import PATH_TO_BIRDLIST_DBCONVERSION
    file = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + COUPLING_FILE)

    csvFileReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')
    nbr_couples_skipped = 0

    # logger
    from birdlist.dbconversion.logger import logger

    lognotes = 'C O U P L I N G   I M P O R T   L O G'
    couple_import_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/coupling_import.log', log_notes=lognotes)
    lognotes = 'C O U P L I N G   I M P O R T   E R R O R - L O G'
    couple_import_ERROR_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/coupling_import_ERROR.log', log_notes=lognotes)
    lognotes = 'C O U P L I N G   N o   G E N E R A T I O N S - C O N S I S T E N C Y - L O G'
    couple_numgen_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/coupling_numgen.log', log_notes=lognotes)
   
    # move throug the rows -> individual couplings
    for row in csvFileReader:

        # ---------------------------------
        if debug:
            print row
        # ---------------------------------

        # ID, Male, Female, Cage, Coupling Date, Separation Date, Success, Comment

        import_dict = {}
        import_dict['pk'] = row[0]
        import_dict['male'] = row[1]
        import_dict['female'] = row[2]
        import_dict['cage'] = row[3]
        import_dict['coupling_date'] = row[4]
        import_dict['separation_date'] = row[5]
        import_dict['generations'] = row[6]
        import_dict['comment'] = row[7]

        # ignore the first row
        if import_dict['pk'].__contains__('ID'):
            print 'skipping first line (header)'
            continue

        # ignore couples where either male or female is empty
        if import_dict['male'] == '' or import_dict['female'] == '':
            print 'can not import empty couple: ' + import_dict['pk']
            nbr_couples_skipped = nbr_couples_skipped + 1
            couple_import_ERROR_log.write_string_to_log('could not import couple ' + import_dict['pk'] +' (male: ' + import_dict['male'] + ', female: ' + import_dict['female'] + ') because of EMPTY STRING')
            continue

        # try to find male / female in db
        male_obj = find_bird_obj(import_dict['male'])
        female_obj = find_bird_obj(import_dict['female'])

        # if we cannot find either of them we do not create couple
        if male_obj == None or female_obj == None:
            print 'can not import this coupling session - bird not found: ' + import_dict['pk']
            nbr_couples_skipped = nbr_couples_skipped + 1
            couple_import_ERROR_log.write_string_to_log('could not import couple ' + import_dict['pk'] +' (male: ' + import_dict['male'] + ', female: ' + import_dict['female'] + ') because could not find male/female in db')
            continue

        cage_obj = find_cage_id(import_dict['cage'])

        import_dict['coupling_date'] = convert_date(import_dict['coupling_date'])
        import_dict['separation_date'] = convert_date(import_dict['separation_date'])
        import_dict['comment'] = import_dict['comment'].decode("cp1252")

        coupling_id = create_coupling(male_obj, female_obj, cage_obj, import_dict['coupling_date'], import_dict['separation_date'], import_dict['comment'])
        import_dict['id'] = str(coupling_id)
        
        couple_import_log.write_machine_readable_log(import_dict)
        couple_numgen_log.write_string_to_log('coupling id in new db$' + str(coupling_id) + '$number of generations in old db$' + str(import_dict['generations']))


    file.close();

    print 'created new entries'
    print 'a total of: ' + nbr_couples_skipped.__str__() + ' couples could not be imported'



def create_coupling(male, female, cage, coupling_date, separation_date, comment):

    # does this couple already exist?
    a = CoupleLookup.objects.filter(father = male, mother = female)

    if a.__len__() == 0:
        # new couple & couple lookup entry
        couple = Couple()
        couple.save()
        couple_lookup = CoupleLookup(couple = couple, father = male, mother = female)
        couple_lookup.save()

    elif a.__len__() == 1:
        # already known couple
        a = a.get()
        couple = Couple(id = a.couple_id)
        print 'found previously added couple #: ' + a.id.__str__()
    else:
        print 'more than one couplelookup found'
        print a
        return 

    coupling = Coupling(couple = couple, cage = cage, coupling_date = coupling_date, separation_date = separation_date, comment = comment)
    coupling.save()
    
    return coupling.id


def convert_date(string):
    if string == '':
        return None

    import time
    b = time.strptime(string, '%d.%m.%Y')
    string = time.strftime("%Y-%m-%d", b)
    return string


def find_bird_obj(bird_to_find):

    from birdlist.models import Bird
    bird = Bird.objects.filter(name__exact = bird_to_find)
    if bird:
        bird = bird.get()
    else:
        bird = None

    return bird

def find_cage_id(cage_to_find):

    from birdlist.models import Cage
    cage = None
    if cage_to_find:
        cage = Cage.objects.filter(name__exact = cage_to_find)
        if cage:
            cage = cage.get()
        else:
            cage = Cage.objects.filter(function = Cage.FUNCTION_MISSING).get()
    else:
        cage = Cage.objects.filter(function = Cage.FUNCTION_DISPOSAL).get()

    
    return cage

