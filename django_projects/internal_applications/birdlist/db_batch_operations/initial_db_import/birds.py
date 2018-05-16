# make sure to set autoincrement of table to 1 before running this script.
# the raw mysql command: TRUNCATE TABLE `birdlist_bird`
# will get rid of all entries and take care of the autoincrement
# OR DO:
# ALTER TABLE theTableInQuestion AUTO_INCREMENT=1
# but this didn't work for me ...

import datetime
from birdlist.models import User
from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER, BIRDLIST_FILE

IGNORED_BIRDS = ('x', 'xx', 'xxx', 'xxxxx', 'dummy', 'dummy2', '')

def import_birds(debug=0):

    delete_old_entries(debug=debug);
    create_new_entries(debug=debug);
    print 'all done'


def delete_old_entries(debug=0):

    from birdlist.models import Bird
    #for i in Bird.objects.all():
    #   i.delete()

    # kill all data by truncating table
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_bird`')
    cursor.close()
    connection.close()

    print 'deleted old entries'



def create_new_entries(debug=0):

    from birdlist.models import Bird
    import csv
    
    # set up import logs
    from birdlist.dbconversion.logger import logger
    lognotes = 'B I R D L I S T   I M P O R T   L O G   -   H U M A N    R E A D A B L E'
    bird_import_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/bird_import.log', log_notes=lognotes)
    lognotes = 'B I R D L I S T   I M P O R T   L O G   -   M A C H I N E   R E A D A B L E'
    bird_import_mlog = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/bird_import.mlog', log_notes=lognotes)
    lognotes = 'B I R D L I S T   I M P O R T   E R R O R   L O G'
    bird_import_ERROR_log = logger(PATH_TO_BIRDLIST_DBCONVERSION+'log/bird_import_ERROR.log', log_notes=lognotes)
    
    # get birdlist files path and open it
    import_file = PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE
    file = open(import_file)
    
    # and write it into the logs
    bird_import_log.write_string_to_log('imported file: ' + import_file)
    bird_import_ERROR_log.write_string_to_log('imported file: ' + import_file)
    
    # now read and import the data from the csv - file
    csvFileReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')
    nbr_birds_skipped = 0

    # ----------------------------
    if debug:
        print file
    # ----------------------------

    for row in csvFileReader:
        # the rows in the used csv file correspond to birds -> move through all birds
        
        # within this row go through the different fields by increasing index
        index = 0

        # ----------------------------
        if debug:
            print '-----------------------------------'
            print 'row: ' + str(row)
        # ----------------------------

        name = row[index]

        # ignore the first row and any tweak birds and birds in IGNORED_BIRDS
        if name.__contains__('Birdname') or name.upper().__contains__('TWEAK') or name in IGNORED_BIRDS:
            bird_import_ERROR_log.write_string_to_log('not imported - birdname: ' + name)
            print 'do not import bird: ' + name
            nbr_birds_skipped = nbr_birds_skipped + 1
            continue

        index = index + 1
        species = row[index]

        index = index + 1
        sex = row[index]
        if sex == 'M':
            sex = 'm'
        elif sex == 'F':
            sex = 'f'
        elif sex == '':
            sex = 'u'

        index = index + 1
        birthday = row[index]    
        try:
            birthday = convert_date(birthday, debug=debug)
        except:
            birthday = None # if birthday is not of format '%d.%m.%Y' we put it to zero 

        index = index + 1
        uncertainty = row[index]

        if uncertainty and uncertainty.isdigit():
            uncertainty = int(uncertainty)
            uncertainty = uncertainty.__neg__()
        else:
            uncertainty = -8

        index = index + 1
        cage = row[index]
        # there are some wrong cage names in the db that have to be corrected
        if cage:
            if cage[-1] == 'l':
                cage = cage.replace('l', '')
        cage = find_cage_id(cage, debug=debug)

        index = index + 1
        father = row[index]

        '''
        if father == '':
            father = None
        else:
            father = find_bird_id(father)
            if father == None:
                print 'can not import bird: ' + name
                nbr_birds_skipped = nbr_birds_skipped + 1
                continue
        '''

        index = index + 1
        mother = row[index]

        '''
        if mother == '':
            mother = None
        else:
            mother = find_bird_id(mother)
            if mother == None:
                print 'can not import bird: ' + name
                nbr_birds_skipped = nbr_birds_skipped + 1
                continue
        '''
         
        index = index + 1
        exit_date = row[index]
        if exit_date == '':
            exit_date = None
        else:
            exit_date = convert_date(exit_date, debug=debug)

        index = index + 1
        cause_of_exit = row[index]
        cause_of_exit = find_exit_id(cause_of_exit)

        index = index + 1
        comment = row[index]
        if comment == '':
            comment = None
        else:
            # kick out any illegal characters
            comment = comment.decode("cp1252")

        index = index + 1
        reserved = row[index]
        if reserved == 'FALSE':
            reserved = False
        else:
            reserved = True

        if reserved:
            reserved_until = datetime.date(2011,01,31)
            reserved_by = User.objects.get(username='test')
        else:
            reserved_until = None
            reserved_by = None

        import_dict = {}
        import_dict['name'] = name
        import_dict['birthday'] = str(birthday)
        import_dict['uncertainty'] = str(uncertainty)
        import_dict['cage'] = str(cage)
        import_dict['sex'] = str(sex)
        import_dict['species'] = str(species)
        import_dict['reserved'] = str(reserved)
        import_dict['comment'] = str(comment)
        import_dict['exit date'] = str(exit_date)
        import_dict['cause of exit'] = str(cause_of_exit)

        # generate and save bird instance
        a = Bird(name = name, cage = cage, sex = sex, species = species, date_of_birth = birthday,
            comment = comment, exit_date = exit_date, cause_of_exit = cause_of_exit, age_uncertainty = uncertainty,
            reserved_by=reserved_by, reserved_until= reserved_until)

        a.save()

        import_dict['id'] = a.id

        # generate import message 
        import_message = '\n\n' + import_dict['name'] + '\n-----------------------------------\n'
        for item in import_dict:
            import_message = import_message + item + ': ' + str(import_dict[item]) + '\n'
        import_message = import_message + '-----------------------------------\n\n' \

        # ----------------------------
        if debug:
            print import_message
        # ----------------------------

        bird_import_log.write_string_to_log(import_message)
        bird_import_mlog.write_machine_readable_log(import_dict)

    file.close();

    print 'created new entries'
    print 'a total of: ' + nbr_birds_skipped.__str__() + ' birds were not imported'

    bird_import_log.write_string_to_log('## a total of: ' + nbr_birds_skipped.__str__() + ' birds were not imported')


def convert_date(string, debug=0):
    
    # ----------------------------
    if debug:
        print string 
    # ----------------------------
    if string:
        import time
        b = time.strptime(string, '%d.%m.%Y')
        string = time.strftime("%Y-%m-%d", b)
        return string
    else:
        return 


def find_cage_id(cage_to_find, debug=0):

    # ----------------------------
    if debug:
        print 'cage to find: ' + str(cage_to_find)
    # ----------------------------

    from birdlist.models import Cage

    cage = None

    # if cage_to_find is not empty we try to assign a cage in the new db
    if cage_to_find:
       
        # in db existing cages we do not know how to deal with
        if cage_to_find in ('F', '?', '??'):
            cage = Cage.objects.filter(function = Cage.FUNCTION_MISSING).get()

        elif cage_to_find in ('AU-L'):
            cage = Cage.objects.filter(name__exact = 'A-UL').get()

        elif cage_to_find in ('ISO5'):
            cage = Cage.objects.filter(name__exact = 'IS5').get()
        
        elif cage_to_find in ('ISO7'):
            cage = Cage.objects.filter(name__exact = 'IS7').get()
        
        # regular cages
        else:
            cage = Cage.objects.filter(name__exact = cage_to_find)

            # ----------------------------
            if debug:
                print cage
                if cage:
                    a = True
                else:
                    a = False
                print a
            # ----------------------------
            
            if cage != []:
                cage = cage.get()
            else:
                print 'could not find cage in db: ' + cage_to_find
    
    # empty cage fields correspond to dead birds -> DISPOSAL
    else:
        cage = Cage.objects.filter(function = Cage.FUNCTION_DISPOSAL).get()

    
    return cage



def find_exit_id(exit_str):

    from birdlist.models import Bird

    if exit_str == 'NE':
        return Bird.EXIT_NONEXPERIMENTAL
    elif exit_str == 'Given away':
        return Bird.EXIT_GIVENAWAY
    elif exit_str == 'End of Exp.':
        return Bird.EXIT_SLEEP
    elif exit_str == 'Perished':
        return Bird.EXIT_PERISHED
    elif exit_str == 'Surgery':
        return Bird.EXIT_SURGERY
    else:
        return None


