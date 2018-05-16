# make sure to set autoincrement of table to 1 before running this script.
# the raw mysql command: TRUNCATE TABLE `birdlist_cage`
# will get rid of all entries and take care of the autoincrement
# OR DO:
# ALTER TABLE theTableInQuestion AUTO_INCREMENT=1
# but this didn't work for me ...


# ROOMS
    
lab_rooms = (
        ('55 F40', 'Lab1'),
        ('55 F42', 'Lab2'),
        ('55 F54', 'Surgery Room'),
        ('36 F86a', 'Breeding Room #1'),
        ('36 F86', 'Breeding Room #2'),
        ('36 F84', 'Juvenile Isolation Room'),
        ('#', 'no room'),
        )


def populate_rooms(): 
    '''
    delete and populate all lab rooms from scratch to be able to work with a completely clean table
    '''
    # delete all existing rooms in db
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_labroom`')
    cursor.close()
    connection.close()

    # now populate the db with the following rooms
    from birdlist.models import LabRoom
    
    for room in lab_rooms:
        lab_room = LabRoom(room_number=room[0], description=room[1])
        lab_room.save()

    print 'populated LabRooms'


# CAGES

BR1 = ('M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'O1', 'O2', 'O3', 'O4', 'O5', 'O6', 'O7', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', )

BR2 = ('2M1', '2M2', '2M3', '2M4', '2M5', '2O1', '2O2', '2O3', '2O4', '2O5', '2U1', '2U2', '2U3', '2U4', '2U5', '2U6', '2U7',\
        'A', 'A-UL', 'A-UR', 'A-U', 'KM', 'KO', 'KU', )

jIS = ('FJ1', 'FJ1r', 'FJ2', 'FJ2r', 'FJ3', 'FJ3r', 'FJ4', 'FJ4r', 'FJ5', 'FJ5r', 'FJ6', 'FJ6r', 'FJ7', 'FJ7r', 'FJ8', 'FJ8r',)

LAB1 = ('E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14',)
LAB2 = ('IS1', 'IS2', 'IS3', 'IS4', 'IS5', 'IS6', 'IS7', 'IS8', 'IS9', 'IS10', )

SURG = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'MK', )

OLD = ('ZZ1', 'ZZ2', 'ZZ-M', 'ZZ-U', 'ZZ-O',\
        'M1B', 'M2B', 'M3B', 'M4B', 'M5B', 'M6B', 'M7B', 'O1B', 'O2B', 'O3B', 'O4B', 'O5B', 'O6B', 'O7B', 'U1B', 'U2B', 'U3B', 'U4B', 'U5B', 'U6B', 'U7B',\
        '2M1B', '2M2B', '2M3B', '2M4B', '2M5B', '2O1B', '2O2B', '2O3B', '2O4B', '2O5B', '2U1B', '2U2B', '2U3B', '2U4B', '2U5B', '2U6B', '2U7B', 'R0', 'R0B', )


from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, CAGES_FILE, DELIMITER


def import_cages(debug=0):

    delete_old_entries();
    create_new_entries(debug=debug);
    print 'all done'


def delete_old_entries():

    # delete all existing rooms in db
    from django.db import connection
    cursor = connection.cursor()        
    cursor.execute('TRUNCATE TABLE `birdlist_cage`')
    cursor.close()
    connection.close()

    print 'deleted old entries'


def create_new_entries(debug=0):

    from birdlist.models import Cage
    import csv
    file = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + CAGES_FILE)

    if debug:
        print file

    testReader = csv.reader(file, delimiter = DELIMITER, quotechar = '"')

    for row in testReader:
        if debug:
            print row

        # discard the following cages out of different reasons 
        # Cage : belongs to the first line with attribute names
        # LAB1, LAB2 are incomplete in import-file
        if row[0] in ('Cage', ) or row[0] in LAB2 or row[0]  in LAB1:
            continue

        name = row[0]
        occupancy = int(row[1])
         
        if name in BR1:
            function = Cage.FUNCTION_BREEDING
            room = 4
        
        elif name in BR2:
            if name in ('A-UR', 'A-UL'):
                function = Cage.FUNCTION_BREEDINGBREAK
            elif name in ('A'):
                function = Cage.FUNCTION_LONGTERMSTORAGE
            else:
                function = Cage.FUNCTION_BREEDING
            room = 5

        elif name in jIS:
            function = Cage.FUNCTION_ISOLATIONDEVELOPMENTAL
            room = 6

        elif name in LAB2:
            function = Cage.FUNCTION_ISOLATIONRECORDINGS
            room = 2

        elif name in LAB1:
            function = Cage.FUNCTION_CHRONICEXPERIMENT
            room = 1

        elif name in SURG:
            function = Cage.FUNCTION_TEMPORARYSTORAGE
            room = 3
            occupancy = 5

        elif name in OLD:
            function = Cage.FUNCTION_NOTUSEDANYMORE
            room = 7

        else:
            print 'could not assign cage: ' + name
            

        a = Cage(name = name, max_occupancy = occupancy, function = function, room_id = room)
        a.save(); 
        print 'created cage: ' + name

    file.close();
    
    # the so far empty cages
    a = Cage(name = 'OutOfColony', max_occupancy = 1000000, function = Cage.FUNCTION_DISPOSAL, room_id = 7)
    a.save()
    print 'created cage: Cemetery'

    # we do not use a missing cage anymore, missing birds get a cause_of_exit 'Missing'
    a = Cage(name = 'Missing', max_occupancy = 100, function = Cage.FUNCTION_MISSING, room_id = 7)
    a.save()
    print 'created cage: Missing' 

    # the two extra R -cages
    a = Cage(name = 'R0', max_occupancy = 14, function = Cage.FUNCTION_NOTUSEDANYMORE, room_id = 3)
    a.save()
    print 'created cage: R0'

    a = Cage(name = 'R0B', max_occupancy = 7, function = Cage.FUNCTION_NOTUSEDANYMORE, room_id = 3)
    a.save()
    print 'created cage: R0B'

    # since the E - setups are not in the access db cages - table but there are birds in these setups we need to add them as well here
    for setup in LAB1:
        name = setup
        function = Cage.FUNCTION_CHRONICEXPERIMENT
        room = 1
        occupancy = 2
        a = Cage(name = name, max_occupancy = occupancy, function = function, room_id = room)
        a.save(); 
        print 'created cage: ' + name

    for setup in LAB2:
        name = setup
        function = Cage.FUNCTION_ISOLATIONRECORDINGS
        room = 2
        occupancy = 2
        a = Cage(name = name, max_occupancy = occupancy, function = function, room_id = room)
        a.save(); 
        print 'created cage: ' + name


    for cage in jIS:
        if Cage.objects.filter(name=cage):
            continue
        else:
            name = cage
            function = Cage.FUNCTION_ISOLATIONDEVELOPMENTAL
            room = 6
            occupancy = 6
            a = Cage(name = name, max_occupancy = occupancy, function = function, room_id = room)
            a.save(); 
            print 'created cage: ' + name


    print 'created new entries'

