# make sure to set autoincrement of table to 1 before running this script.
# the raw mysql command: TRUNCATE TABLE `birdlist_bird`
# will get rid of all entries and take care of the autoincrement
# OR DO:
# ALTER TABLE theTableInQuestion AUTO_INCREMENT=1
# but this didn't work for me ...

def import_birds():

    delete_old_entries();
    create_new_entries();
    print 'all done'



def delete_old_entries():

    from birdlist.models import Bird
    for i in Bird.objects.all():
        i.delete()

    print 'deleted old entries'

def create_new_entries():

    from birdlist.models import Bird
    import csv
    file = open("/home/db/django/django_projects/internal_applications/birdlist/dbconversion/Birdlist.csv")
    #file = open("/home/kotowicz/local/code/django/django_projects/internal_applications/birdlist/dbconversion/Birdlist.csv")

    testReader = csv.reader(file, delimiter = ',', quotechar = '"')
    nbr_birds_skipped = 0

    for row in testReader:
        pk = row[0]
        name = row[1]
        # ignore the first row and any tweak birds
        if name.__contains__('Birdname') or name.upper().__contains__('TWEAK') or name == '':
            print 'can not import bird: ' + name
            nbr_birds_skipped = nbr_birds_skipped + 1
            continue


        species = row[2]
        sex = row[3]
        birthday = row[4]

    
        if birthday == '':
            birthday = '2007-12-24'

        uncertainty = row[5]

        if uncertainty and uncertainty.isdigit():
            uncertainty = int(uncertainty)
            uncertainty = uncertainty.__neg__()
        else:
            uncertainty = 0

        cage = row[6]
        cage = find_cage_id(cage)
        father = row[7]

        if father == '':
            father = None
        else:
            father = find_bird_id(father)
            if father == None:
                print 'can not import bird: ' + name
                nbr_birds_skipped = nbr_birds_skipped + 1
                continue

        mother = row[8]

        if mother == '':
            mother = None
        else:
            mother = find_bird_id(mother)
            if mother == None:
                print 'can not import bird: ' + name
                nbr_birds_skipped = nbr_birds_skipped + 1
                continue
         
        exit_date = row[9]
        if exit_date == '':
            exit_date = None

        cause_of_exit = row[10]
        cause_of_exit = find_exit_id(cause_of_exit)

        comment = row[11]
        if comment == '':
            comment = None
        else:
            # kick out any illegal characters
            comment = comment.decode("cp1252")


        reserved = row[12]
        reserved = bool(int(reserved))

        a = Bird(name = name, birthday = birthday, age_uncertainty = uncertainty, 
            cage = cage, sex = sex, species = species, father = father, mother = mother, 
            reserved = reserved, comment = comment, exit_date = exit_date, cause_of_exit = cause_of_exit)

        a.save(); 

    file.close();

    print 'created new entries'
    print 'a total of: ' + nbr_birds_skipped.__str__() + ' birds could not be imported'


def find_bird_id(bird_to_find):

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


