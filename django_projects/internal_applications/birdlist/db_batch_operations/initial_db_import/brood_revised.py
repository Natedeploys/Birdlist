
# Introductory Notes August 17th 2010
# --------------------------------------------------------------------
# I changed the Bird model to include the birthday. I consider it to be an attribute of single bird.
# In the case we would switch to exact birthdays or the case of bought birds we run into problems
# otherwise.
# We'll have to guarantee data consistency via input checks ..

# We will nevertheless keep the Brood entity to contain siblings from within the same generation
# or birds that were bought/obtained together.

# To populate the Broods and to connect them with the Couplings a different approach
# is therefore necessary:
# - go through all Couplings and find all Birds that could be offspring of it.
# - order them by age and start with the oldest one. 
# - create a Brood for this one and connect it with the Coupling.
# - loop / go to next:
#           if born within birthday_tolerance days add to previous Brood
#               -> update birthday to oldest, if necessary
#               -> correct uncertainty for all birds in brood
#           else: create new Brood
#
# -> with this procedure we miss roughly 260 birds
# - loop through all birds that do not have a brood assigned yet:
#           see at their comment to figure out if they were bought
#           -> create purchase event brood via day of purchase and supplier
#           -> #TODO: i'm not sure yet, whether i want to create a Couple for different vendors ..



from birdlist.models import Couple, Coupling, Brood, CoupleLookup, Bird, Cage
from coupling import find_bird_obj
from coupling import create_coupling

from birdlist.dbconversion.settings import PATH_TO_BIRDLIST_DBCONVERSION, DELIMITER,\
        BIRDLIST_FILE, COUPLING_FILE, BIRTHDAY_TOLERANCE

from birdlist.dbconversion.birds import IGNORED_BIRDS

import time, datetime


# ---------------------------------------------------------------------
def generate_broods(debug=0, birthday_tolerance=BIRTHDAY_TOLERANCE):
    '''
    the overall procedure
    '''
    delete_old_entries(debug=debug)
    create_broods_for_couplings(debug=debug, birthday_tolerance=birthday_tolerance)

    print 'all done'

    return 


# ---------------------------------------------------------------------
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
    
    return


def create_broods_for_couplings(debug=0, birthday_tolerance=10):
    '''
    '''

    import csv

    all_couplings = Coupling.objects.all()
    
    for current_coupling in all_couplings:

        # ---------------------------------
        if debug:
            print '\n\n----------------------------'
            print current_coupling
        # ---------------------------------


        couplings_offspring = []
        
        mum = current_coupling.couple.get_female()
        dad = current_coupling.couple.get_male()

        # the to be imported birds
        csvfile = open(PATH_TO_BIRDLIST_DBCONVERSION + 'data/' + BIRDLIST_FILE)
        fileReader = csv.reader(csvfile, delimiter = DELIMITER, quotechar = '"')

        # now find all birds that are offspring of the current couple
        for birdy in fileReader:

            # ordered list of csv row attributes
            import_list = ['name', 'species', 'sex', 'birthday', 'uncertainty', 'cage',\
                    'father', 'mother', 'exit date', 'cause of exit', 'comment', 'reserved', ]

            # fill in bird-container
            bird = {}
            for i, item in enumerate(import_list):
                bird[item] = str(birdy[i])

            # compare this birds/birdies mum and dad with our current couplings 
            if bird['mother'] == mum.name and bird['father'] == dad.name:

                django_bird = Bird.objects.get(name=bird['name'])
                if current_coupling.separation_date:
                    sep_date = current_coupling.separation_date
                else:
                    sep_date = datetime.date.today()

                if django_bird and date_is_within_dates(django_bird.date_of_birth.isoformat(), \
                        current_coupling.coupling_date.isoformat(), sep_date.isoformat()) :

                    couplings_offspring.append(django_bird)
                else:
                    # this is not valable canditate then ..
                    continue

       
        csvfile.close()

        # sort these birds according to age
        # it would be nicer to use a django QuerySet and use its sort function, but here
        # this was the quicker solution
        couplings_offspring.sort(key=lambda x: x.date_of_birth.toordinal(), reverse=False)

        # ---------------------------------
        if debug:
            print couplings_offspring 
        # ---------------------------------

        # now go through these birds and assign or create a brood for each individual one
        for offspring in couplings_offspring:

            # find existing broods of the current coupling
            existing_broods = Brood.objects.filter(coupling=current_coupling)

            # if there are no broods generate a new one
            if existing_broods.__len__() == 0:
                new_brood = Brood(coupling=current_coupling, origin=Brood.ORIGIN_BREEDING)
                new_brood.save()
                offspring.brood = new_brood
                offspring.save()
                # ---------------------------------
                if debug:
                    print 'new brood generated'
                # ---------------------------------
                continue

            # otherwise find a brood we could assign offspring to
            else:
                brood_assigned = False
                for brood in existing_broods:

                    # prepare some dates for birthday tolerance range
                    end_of_range = datetime.date
                    end_of_range = datetime.date.fromordinal(offspring.date_of_birth.toordinal() + BIRTHDAY_TOLERANCE)
                    
                    # now see whether we have birds that are within BIRTHDAY_TOLERANCE
                    same_hatch_birds = Bird.objects.filter(brood=brood, date_of_birth__range=\
                            (offspring.date_of_birth, end_of_range))
                    # ---------------------------------
                    if debug:
                        print same_hatch_birds
                    # ---------------------------------

                    # if they exist these birds should now all have the same date of birth
                    # their all database brosis so we can assign the same brood to offspring
                    if same_hatch_birds.__len__() > 0:
                        # jump out if brood is already assigned at earlier stage ..
                        if brood_assigned:
                            # ---------------------------------
                            if debug:
                                print 'brood already assigned'
                            # ---------------------------------
                            continue
                        offspring.brood = brood
                        ######################################
                        # It has been decided in group meeting 14/10/15, that the uncertainty should not be corrected.
                        # The reason is that Heiko is now checking for newborns more often than it used to be, and he can therefore adjust uncertainties
                        # better himself. Next 8 lines have been commented out. Patch suggested on 23/10/15 by templier@ini.ethz.ch
                        
                        # # we also have to check the uncertainty (for all birds in brood)
                        # temp_uncertainty = abs(same_hatch_birds[0].date_of_birth.toordinal()-offspring.date_of_birth.toordinal())
                        # if temp_uncertainty.__neg__() < offspring.age_uncertainty:
                            # same_hatch_birds.update(age_uncertainty = temp_uncertainty.__neg__())
                            # # ---------------------------------
                            # if debug:
                                # print 'uncertainty corrected'
                            # # ---------------------------------
                        ######################################
                        offspring.date_of_birth = same_hatch_birds[0].date_of_birth
                        offspring.save()
                        # ---------------------------------
                        if debug:
                            print 'offspring assigned to brood'
                        # ---------------------------------
                        brood_assigned = True
                        continue
                
                # if we have not assigned a brood by now, we still have to create one!
                if not brood_assigned:
                    new_brood = Brood(coupling=current_coupling, origin=Brood.ORIGIN_BREEDING)
                    new_brood.save()
                    offspring.brood = new_brood
                    offspring.save()
                    # ---------------------------------
                    if debug:
                        print 'ultima ratio brood generated'
                    # ---------------------------------




def date_is_within_dates(date_string, start_string, end_string):
    '''
    enter date strings in isoformat YYYY-MM-DD as strings
    and check whether date is within start and end
    return True or False
    '''

    date = time.mktime(time.strptime(date_string, "%Y-%m-%d"))
    start = time.mktime(time.strptime(start_string, "%Y-%m-%d"))
    
    if end_string != None:
        end = time.mktime(time.strptime(end_string, "%Y-%m-%d"))
    else:
        return False
   
    if end < start:
        raise NameError('you entered an end_date that is smaller than the start_date!')
    
    if date<=end and date>=start:
        return True
    else:
        return False

