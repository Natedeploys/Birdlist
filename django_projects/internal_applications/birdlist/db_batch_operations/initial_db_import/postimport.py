# a set of function allowing acces to the imported data
# and correction algorithms for imported inconsistent data

import datetime

from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, BIRDLIST_FILE, DELIMITER

from birdlist.models import Bird, Cage, Activity


def read_file_into_list(filepath):
    '''
    open a file read lines into list and rsplit it
    '''
    file_content = []
    readfile = open(filepath)
    for line in readfile.readlines():
        file_content.append(line.rsplit(DELIMITER))

    return file_content
    

def get_old_bird_info(birdname):
    '''
    finds the bird in the imported birdlist and returns a
    dict containing the old information
    '''

    # get birdlist files path and open it
    import_file = PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE
    
    file_content = read_file_into_list(import_file)

    bird_info_items = ['name', 'species', 'sex', 'birthday', 'uncertainty',
            'cage', 'father', 'mother', 'exit date', 'cause of exit', 'comment', 'reserved', ]

    for line in file_content:
        if line[0] == birdname:
            bird_info = {}
            for i, item in enumerate(bird_info_items):
                bird_info[item] = line[i]
            return bird_info

    return 'info about the bird you requested ( %s ) was not found' % birdname


def compare_bird_data_tofile(birds):
    '''
    '''
    string_to_write = ''

    for bird in birds:
        old_bird = get_old_bird_info(bird.name)
        if not (old_bird['father'] and old_bird['mother']):
           continue
        if old_bird['exit date']:
            continue
        if old_bird['name'][0]=='d':
            continue
        string_to_write += '\n\n'
        string_to_write += 'name\t\t\t' + bird.name + '\t\t\t' + old_bird['name'] + '\n'
        string_to_write += '----------------------------------------------------' + '\n'
        string_to_write += 'species\t\t\t' + bird.species + '\t\t\t\t' + old_bird['species'] + '\n'
#       string_to_write += 'sex\t\t' + bird.sex + '\t\t' + old_bird['sex'] + '\n'
        string_to_write += 'birthday\t\t' + str(bird.date_of_birth) + '\t\t' + old_bird['birthday'] + '\n'
#       string_to_write += 'uncertainty\t\t' + str(bird.age_uncertainty) + '\t\t' + old_bird['uncertainty'] + '\n'
        string_to_write += 'cage\t\t\t' + str(bird.cage.name) + '\t\t\t\t' + old_bird['cage'] + '\n'
        string_to_write += 'father\t\t\t' + str(bird.get_father()) + '\t\t\t' + old_bird['father'] + '\n'
        string_to_write += 'mother\t\t\t' + str(bird.get_mother()) + '\t\t\t' + old_bird['mother'] + '\n'
        string_to_write += 'exit date\t\t' + str(bird.exit_date) + '\t\t\t' + old_bird['exit date'] + '\n'
        string_to_write += 'cause\t\t\t' + str(bird.get_cause_of_exit_display()) + '\t\t\t' + old_bird['cause of exit'] + '\n'
        string_to_write += 'new comment\n' + str(bird.comment) + '\n'
        string_to_write += 'old comment\n' + old_bird['comment'] + '\n'


    outputpath = PATH_TO_BIRDLIST_DBCONVERSION + 'birds_to_compare.txt'
    outputfile = open(outputpath, 'w')

    outputfile.write(string_to_write)

    outputfile.close()


def write_parental_info_into_no_brood_birds(save=False):
    '''
    for dead birds that have some information about their parents but this information
    could not be assigned to a couple/coupling we write it into their comment
    field, such that we do not loose this it completely.

    tested, works. michael, 22.01.2011
    executed, 23.01.2011 - 11:10 PM
    '''
    no_brood_birds = Bird.objects.filter(brood=None)

    counter = 0

    for bird in no_brood_birds:
        old_bird = get_old_bird_info(bird.name)
        if old_bird['mother'] or old_bird['father']:
            comment = bird.comment
            parental_text = '-----------------------------------------------\n' +\
                        'Somehow this birds parental information was inconsistent.\n' +\
                        'We could not automatically assign a couple when importing the data.\n' +\
                        'In the old birdlist this birds parents were:\n' +\
                        'father: %s \tmother: %s ' % (str(old_bird['father']), str(old_bird['mother']))
            if comment:
                comment = comment + '\n\nold birdlist parental information\n' + parental_text 
            else:
                comment = 'old birdlist parental information\n' + parental_text
            
            bird.comment = comment
            if save:
                bird.save()
            print
            print
            print '-----------------------------', bird.name
            print comment

        counter += 1

    print 'done'
    print 'number of birds with added comment: ', counter
    print 'number of birds without brood: ', no_brood_birds.count()



def set_cage_to_OutOfColony_for_dead_birds_in_other_cage(save=False):
    '''
    the followin birds are not in OutOfColony even though they
    have an exit date (even a cause of exit):

    o8r12
    Missing
    2010-05-07
    end of experiment (chronic / acute sleep)

    p13r8
    KO
    2010-09-03
    end of experiment (chronic / acute sleep)

    p5r8
    KM
    2009-11-13
    end of experiment (chronic / acute sleep)

    r14s12
    KU
    2010-09-16
    not experimental

    -> set their cage to OutOfColony

    tested, works. michael, 21.01.2011
    executed, 23.01.2011 - 11:10 PM
    '''
    oocc = Cage.objects.get(name='OutOfColony')

    dead_birds = Bird.objects.exclude(exit_date=None)
    dead_birds_in = dead_birds.exclude(cage__name='OutOfColony')

    for bird in dead_birds_in:
        bird.cage = oocc
        if save:
            bird.save()

        print 
        print 'bird: ', bird.name


def birds_no_exit_date_out(save=False): 
    '''
    birds that have no exit_date but are OutOfColony need to be corrected

    there are multiple possibilities here:

    bird has no exit date and is 'OutOfColony' and
    - has an experiment with an end_date
    - has a cause_of_exit!=None
    => make exit_date = end_date of last experiment

    - has birthday
    - has 'dJ' in name
    => set end_of_experiment to 20 dph, this is kinda arbitray of course
        the reason though is that most probably this was due to miscounting
        which should have to be found out after 20dph ?!

    - has an experiment with an end_date
    - no cause_of_exit
    => have look at comment: experiment could be a SR and bird missing

    - has no experiment
    - has or does not have transfer
    => have look at comment: bird is most probably missing => figure out since when

    most probably there are a few more that have to be looked at individually

    in all cases we write what we changed into the comment field

    the first two can be fixed automatically first for the others we will have to have
    an interactive procedure

    tested, works. michael, 22.01.2011
    executed, 23.01.2011 - 11:12 PM
    '''
    birds_alive_out = Bird.objects.filter(exit_date=None, cage__name='OutOfColony')

    for bird in birds_alive_out:
        trans = Activity.objects.filter(bird=bird, activity_type__name='Cage Transfer').order_by('end_date').reverse()
        exps = Activity.objects.filter(bird=bird, activity_type__name='Experiment').order_by('end_date').reverse()

        '''
        - has an experiment with an end_date
        - has a cause_of_exit!=None
        => make exit_date = end_date of last experiment
        '''
        if exps and bird.cause_of_exit != None:
            bird.exit_date = exps[0].end_date
            comment_text = 'exit_date was None and automatically set to end_date of last experiment after data import\n' +\
                    'because bird was OutOfColony and had a cause_of_exit but no exit date!'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist inconsisteny notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist inconsisteny notification ----------------\n' + comment_text

            if save:
                bird.save()

            print 
            print bird.name + ' -----------------------------------'
            print 'fixed as adult with finished experiment'

        elif ('J' in bird.name) and bird.date_of_birth:
            
            bird.exit_date = bird.date_of_birth + datetime.timedelta(20)

            comment_text = 'exit date was automatically set to 20 dph after data import\n' +\
                    'because bird was OutOfColony and had name like a dead juvenile (dJ in it)!'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist inconsisteny notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist inconsisteny notification ----------------\n' + comment_text

            if save:
                bird.save()

            print 
            print bird.name + ' -----------------------------------'
            print 'fixed as juvenile'

        else:

            print 
            print bird.name + ' -----------------------------------'
            print 'no fix yet'
            print bird.date_of_birth
            print 'J' in bird.name


def fix_remaining_no_exit_date_birds(save=False):
    '''
    !!! run  birds_no_exit_date_out() first !!!
    and read explanation in its doc!

    we take here care for the following birds:
    - has an experiment with an end_date
    - no cause_of_exit
    => have look at comment: experiment could be a SR and bird missing

    - has no experiment
    - has or does not have transfer
    => have look at comment: bird is most probably missing => figure out since when

    most probably there are a few more that have to be looked at individually

    in all cases we write what we changed into the comment field

    birds that went missing are cleaned out with separate process that will be implemented
    generally

    tested, works. michael, 22.01.2011
    executed, 23.01.2011 - 11:20 PM
    '''
    birds_alive_out = Bird.objects.filter(exit_date=None, cage__name='OutOfColony', missing_since=None)

    for bird in birds_alive_out:
        trans = Activity.objects.filter(bird=bird, activity_type__name='Cage Transfer').order_by('end_date').reverse()
        exps = Activity.objects.filter(bird=bird, activity_type__name='Experiment').order_by('end_date').reverse()
        
        print
        print
        print bird.name + '---------------------------------'

        if exps:
            print 'EXPERIMENT'
            print exps[0].activity_content
            print 'end date: ', exps[0].end_date
            print 'comment'
            print bird.comment

        elif trans:
            print 'TRANSFER'
            print 'end date: ', trans[0].end_date
            print 'comment'
            print bird.comment

        else:
            print 'NO EXPERIMENT & NO TRANSPORT'
            print 'comment'
            print bird.comment

        what_to_do = raw_input('\nplease indicate what procedure to take to set the exit date:\n' + \
                               'e - the end date of the last experiment\n' + \
                               'm - bird is missing (dd.mm.yyyy)\n' + \
                               'mt - bird is missing - no date -> since last transfer\n' + \
                               'g - bird was given away (dd.mm.yyyy)\n' + \
                               's - skip this bird for now\n' + \
                               '$: ')

        if what_to_do == 'e':
            print '\ntake end_date of last experiment as exit_date'
            bird.exit_date = exps[0].end_date
            bird.cause_of_exit = bird.EXIT_SLEEP

            comment_text = 'exit_date was set to last experiment and cause_of_exit was set to experimental. \n' +\
                    'bird was OutOfColony had no cause_of_exit but an experiment that seemed to be final.'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist inconsisteny notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist inconsisteny notification ----------------\n' + comment_text

        elif what_to_do == 'm':
            print '\nbird is missing' 
            missing_since = raw_input('since when is this bird missing? (dd.mm.yyyy): ')
            DD, MM, YYYY = missing_since.rsplit('.')
            ms_date = datetime.date(int(YYYY), int(MM), int(DD))
            print 'missing since: ', ms_date
            bird.missing_since = ms_date

            comment_text = 'comment field indicated that bird is missing. \n' +\
                    'missing since field was set with according date.'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist notification ----------------\n' + comment_text

        elif what_to_do == 'mt':
            print '\nbird is missing but has no indication since when' 
            ms_date = trans[0].end_date
            print 'missing since: ', ms_date
            bird.missing_since = ms_date

            comment_text = 'comment field indicated that bird is missing. \n' +\
                    'missing since field was set with date of last transfer.'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist notification ----------------\n' + comment_text

        elif what_to_do == 'g':
            print '\nbird was given away' 
            missing_since = raw_input('when was the bird given away? (dd-mm-yyyy): ')
            DD, MM, YYYY = missing_since.rsplit('.')
            ga_date = datetime.date(int(YYYY), int(MM), int(DD))
            print 'given away on: ', ga_date
            bird.exit_date = ga_date
            bird.cause_of_exit = bird.EXIT_GIVENAWAY

            comment_text = 'comment field indicated that bird was given away. \n' +\
                    'exit date was set to last transfer date and EXIT_GIVENAWAY.'

            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist notification ----------------\n' + comment_text

        elif what_to_do == 's':
            print '\nskip this bird for now' 

        else:
            print 'STUPID!'

        if save:
            bird.save()


        # we do now have to figure out which birds are out of colony and missing 
        # is it possible that they are OutOfColony or do they have to have a cage? YES, this has to be possible
        # run the missing birds data maintenance function in utils ...


def set_licence_for_user(user, licence, save=False):
    '''
    '''
    user_experiments = Activity.objects.filter(user=user, activity_type__name='Experiment')
    
    for exp in user_experiments:
        exp.animal_experiment_licence = licence
        
        if save:
            exp.save()

    print 'done!'


# MISSING BIRDS

def remove_birds_from_missing_cage(save=False):
    '''
    '''

    birds_in_missing_cage = Bird.objects.filter(cage__name='Missing')

    for bird in birds_in_missing_cage:
        trans = Activity.objects.filter(bird=bird, activity_type__name='Cage Transfer').order_by('end_date').reverse()

        print
        print
        print bird.name + '---------------------------------'

        if trans:
            print 'TRANSFER'
            print 'end date: ', trans[0].end_date
            print 'end date: ', trans[0].activity_content
            print 'comment'
            print bird.comment

        else:
            print 'NO TRANSFER'
            print 'comment'
            print bird.comment

        what_to_do = raw_input('\nplease indicate what procedure to take to set the missing date:\n' + \
                               'm - bird is missing (dd.mm.yyyy)\n' + \
                               'mt - bird is missing - no date -> since last transfer\n' + \
                               's - skip this bird for now\n' + \
                               '$: ')

        if what_to_do == 'm':
            print '\nbird is missing' 
            missing_since = raw_input('since when is this bird missing? (dd.mm.yyyy): ')
            DD, MM, YYYY = missing_since.rsplit('.')
            ms_date = datetime.date(int(YYYY), int(MM), int(DD))
            print 'missing since: ', ms_date
            bird.missing_since = ms_date
            bird.cage = Cage.objects.get(name='OutOfColony')

            comment_text = 'comment field indicated that bird is missing. \n' +\
                    'missing since field was set with according date.'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist notification ----------------\n' + comment_text

        elif what_to_do == 'mt':
            print '\nbird is missing but has no indication since when' 
            ms_date = trans[0].end_date
            print 'missing since: ', ms_date
            bird.missing_since = ms_date
            bird.cage = Cage.objects.get(name='OutOfColony')

            comment_text = 'comment field indicated that bird is missing. \n' +\
                    'missing since field was set with date of last transfer.'
            if bird.comment:
                bird.comment = bird.comment + '\n\nold birdlist notification ----------------\n' + comment_text
            else:
                bird.comment = 'old birdlist notification ----------------\n' + comment_text

        elif what_to_do == 's':
            print '\nskip this bird for now' 

        if save:
            bird.save()


# now we run the clean_out_missing_birds database maintenance function
# then we take care for the birds that still need a cage manually
# move back to old cage (before transfer)
# remove transfer
