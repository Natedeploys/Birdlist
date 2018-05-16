#
# settings for data import
# --------------------------------------------------

# path to dbconversion directory in platform dependent way 
import socket
this_host = socket.gethostname()
if this_host == 'zailor':
    PATH_TO_BIRDLIST_DBCONVERSION = '/data/programming/django/code/django_projects/internal_applications/birdlist/dbconversion/'
    print
    print 'you are importing data on ZAILOR'
elif this_host == 'dude.local':
    PATH_TO_BIRDLIST_DBCONVERSION = '/Users/michael/Documents/00_PhD/10_PROGRAMMING/songbirddjango/code/django_projects/internal_applications/birdlist/dbconversion/'
    print
    print 'you are importing data on DUDE'
elif this_host == 'zubreit':    
    PATH_TO_BIRDLIST_DBCONVERSION = '/local/code/django/django_projects/internal_applications/birdlist/dbconversion/'
else:
    print 'hey man - specify your platform settings in birdlist/dbconversion/settings.py to run this import scripts'
#file = open("/home/db/django/django_projects/internal_applications/birdlist/dbconversion/Birdlist.csv")
#file = open("/local/home/koto/code/django/django_projects/internal_applications/birdlist/dbconversion/Birdlist.csv")
#file = open("/home/kotowicz/local/code/django/django_projects/internal_applications/birdlist/dbconversion/Birdlist.csv")

# the delimeter character in the access exported csv-files
DELIMITER = ';'

# the names of the files that are in involved in import session
# the import scripts are only able to handle .csv files (exports from access db)

BIRDLIST_FILE = 'Birdlist_20110114_1410PM.csv'
CAGE_HISTORY_FILE = 'CageHistory_20110114_1410PM.csv'
CAGES_FILE = 'Cages_20110114_1412PM.csv'
COUPLING_FILE = 'Coupling_20110114_1413PM.csv'
EXP_HISTORY_FILE = 'ExpHistory_20110114_1415PM.csv'

# BROOD GENERATION
# number of days tolerance between birthdays to assign birds still to the same brood
from birdlist.models import Brood # BROOD_RANGE is 10
BIRTHDAY_TOLERANCE = Brood.BROOD_RANGE
# for birthday tolerance 20 we get 29 broods that have different birthdays
# their max_min_diffs are as follows:
# 4 1 1 5 10 4 1 17 5 1 3 1 5 10 7 1 1 1 3 1 6 1 1 2 8 1 1 3 1
# -> only one is bigger than 10, i.e. 17 -> 10 seems to be a reasonable threshold

# users to be added to be added to the database
# last element of every user includes versions of names as they are found in the old access db
USERS = (
        ('michael', 'Michael', 'Graber', 'michael@ini.phys.ethz.ch', True, ('michael', 'michi', 'micheal', )),
        ('kotowicz', 'Andreas', 'Kotowicz', 'kotowicz@ini.phys.ethz.ch', True, ('andreas', 'koto', 'andreas&claude', )),
        ('rich', 'Richard', 'Hahnloser', 'rich@ini.phys.ethz.ch', True, ('rich', 'richard', 'richi', 'aymrich', 'aymrigio',\
                'aymrichgio', )),
        ('georg', 'Georg', 'Keller', 'georg@ini.phys.ethz.ch', False, ('georg', )), 
        ('katja', 'Katja', 'Naie', 'katja@ini.phys.ethz.ch', False, ('katja', )), 
        ('claude', 'Claude', 'Wang', 'cwang@ini.phys.ethz.ch', False, ('claude', 'cllaude', 'Claude', )),
        ('josh', 'Joshua', 'Herbst', 'herbst@ini.phys.ethz.ch', True, ('josh', 'joshua', )),
        ('moritz', 'Moritz', 'Kirschmann', 'moritz@ini.phys.ethz.ch', True, ('moritz', 'moritza', )),
        ('daniele', 'Daniele', 'Oberti', 'doberti@ini.phys.ethz.ch', True, ('daniele', 'doberti', )),
        ('aymeric', 'Aymeric', 'Nager', 'emri@ini.phys.ethz.ch', True, ('emri', 'aymeric', 'aymerik', 'aysep', 'americ',\
                'aysa', 'aymeic', )),
        ('gokcen', 'Gokcen', 'Yildiz', 'gokcen123@gmail.com', False, ('gokcen', )),
        ('jk', 'Joergen', 'Kornfeld', 'joergenk@ini.phys.ethz.ch', True, ('joergen', )),
        ('janie', 'Janie', 'Ondracek', 'janie@ini.phys.ethz.ch', True, ('janie', 'ayjo', 'ayjori', )),
        ('florianh', 'Florian', 'Haering', '########', False, ('florianh', )),
        ('florian', 'Florian', 'Blaettler', 'florian@ini.phys.ethz.ch', True, ('florian', )),
        ('sandra', 'Sandra', 'Wohlgemut', '########', False, ('sandra', )),
        ('michel', 'Michel', 'Schaffner', 'scmichel@student.ethz.ch', False, ('michel', )),
        ('alexei', 'Alexei', 'Vyssotski', 'alexei@ini.phys.ethz.ch', True, ('alexei', 'alexej', 'Alexi', 'alexi', )),
        ('patrick', 'Patrick', 'Ruckstuhl', 'patrick_ruckstuhl@gmx.ch', False, ('patrick', )),
        ('canopoli', 'Alessandro', 'Canopoli', 'canopoli@ini.phys.ethz.ch', True, ('alessandro', )),
        ('fethi', 'Fethi', 'Ramazanoglu', '#########', False, ('fehti', 'fethi' )),
        ('sepehr', 'Sepehr', '########', '#########', False, ('sepehr', )),
        ('kadir', 'Kadir', 'Mutlu', 'kadir@ini.phys.ethz.ch', False, ('kadir', )),
        ('isabelle', 'Isabelle', 'Spuehler', 'ispuehle@student.ethz.ch', False, ('isabelle', )),
        ('yingxue', 'Yingxue', 'Wang', 'yingxue@ini.phys.ethz.ch', False, ('yingxue', )),
        ('sepp', 'Sepp', 'Kollmorgen', 'skollmor@uos.de', True, ('sepp', )),
        ('lisa', 'Lisa', 'Kolb', 'lisa@ini.phys.ethz.ch', True, ('lisa', )),
        ('nicola', 'Nicola', 'Giret', 'nigiret@ini.phys.ethz.ch', True, ('nicola', 'nicolas', 'Nicolas' )),
        ('balz', 'Balz', 'Dunno', 'dunno@student.ethz.ch', True, ('balz', 'Balz', )),
        ('victor', 'Victor', 'Anisimov', 'v_anisimov@rambler.ru', True, ('victor', )),
        ('unknown', 'Unknown', 'User', '########', False, ('????', '', 'x', 'pi', '?', 'y', 'tierpfleger',\
                'fj5', 'who', 'kate', 'johndoe', '2m2', 'someone', 'Someone', 'ku', 'Ku', '1', )),
        )
