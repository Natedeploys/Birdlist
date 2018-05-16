import datetime
from birdlist.models import Cage, Bird, Activity, Activity_Type, Coupling, Brood, Couple, CoupleLookup
from django.shortcuts import get_object_or_404

def handle_new_juveniles(firstbirthday, lastbirthday, nbr_juveniles, cage, coupling, user):
    ''' 
        default 'add new juveniles' function
    '''

    # most basic check before doing any other lookups.
    if coupling.coupling_date > firstbirthday:
        return 'Sorry, no quantum fluctuation for birds: Juveniles can not be born before the couple got together.'
    
    today = datetime.date.today()
    if firstbirthday > today or lastbirthday > today:
        return 'Sorry, no time travel for birds: Juveniles can not be born in the future.'
    
    alphabetic_letters = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',\
            'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z')

    # see whether brood exists, within BROOD_RANGE, otherwise create new brood
    # the only point of definition of BROOD_RANGE is in models.Bird !!!
    brood = Brood.objects.get_brood_within_broodrange(coupling, lastbirthday)

    if not brood:
        # we have to check here whether if there is no brood, there are still juveniles
        if Bird.objects.filter(name__startswith = Bird.JUVENILE_PREFIX, exit_date = None, cause_of_exit = None, cage = cage):
            # return an 'error' in this case
            return 'Unringed juveniles in cage but new generation was born. Ring and rename old generation first.'

        # set default origin
        origin = Brood.ORIGIN_BREEDING
        # modify origin for foster parents
        if coupling.type == Coupling.COUPLING_TYPE_FOSTER_COUPLE:
            origin = Brood.ORIGIN_FOSTER
        
        brood = Brood(coupling=coupling, origin=origin)
        brood.save()

    # find the broods birds 
    siblings = brood.bird_set.all()

    # check if enough letter from "alphabetic_letters" are left.
    if len(siblings) + nbr_juveniles > len(alphabetic_letters):
        max_nbr_to_add = len(alphabetic_letters) - len(siblings)
        if max_nbr_to_add > 0:
            return 'Too many animals for current naming scheme. You can only add %s animals' % max_nbr_to_add
        else:
            return 'You can not add any more animals to this brood. Max number of animals per brood reached.'

    # if there are already siblings
    if siblings:
        # get birthday
        # this is only safe if data is consistent 
        birthday = siblings[0].date_of_birth
        # new birds cannot be older than existing juveniles
        if firstbirthday < birthday:
            return 'You cannot add a juvenile that is older than the already existing ones.'
        # calculate new uncertainty -> diff returns datetime.timedelta instance
        uncertainty_td = lastbirthday-birthday
        uncertainty = -uncertainty_td.days
        # make its abs bigger or equal to number of birds in brood -1
        if uncertainty > -(siblings.count()+nbr_juveniles-1):
            uncertainty = -(siblings.count()+nbr_juveniles-1)
            # if there were already juveniles in that cage, we assume their 
            # birthday was registered correctly
            #birthday = lastbirthday - datetime.timedelta(abs(uncertainty))
        if uncertainty < -7:
            uncertainty = -8
        # adjust uncertainty for siblings
        for brosis in siblings:
            brosis.age_uncertainty = uncertainty
            # also update birthday, cause it could have changed to ifs ago
            #brosis.date_of_birth = birthday
            brosis.save()
    # no siblings
    else:
        uncertainty_td = lastbirthday-firstbirthday
        uncertainty = -uncertainty_td.days
        # make it smaller or equal to number of birds in brood -1
        if uncertainty > -(siblings.count()+nbr_juveniles-1):
            uncertainty = -(siblings.count()+nbr_juveniles-1)
            new_birthday = lastbirthday - datetime.timedelta(abs(uncertainty))
        else:
            new_birthday = today
        if uncertainty < -7:
            uncertainty = -8
        if new_birthday > firstbirthday: 
            birthday = firstbirthday
        else:
            birthday = new_birthday


   
    # now create the new birds using the correct alphabetic letters at the end
    if not siblings:
        startcount = 1
    else:
        startcount = siblings.count()+1

    for newcount in range(startcount, startcount+nbr_juveniles):
        
        bird_specs = {
                'name' : Bird.JUVENILE_PREFIX+cage.name+alphabetic_letters[newcount-1],
                'species' : coupling.couple.get_male().species,
                'sex' : Bird.SEX_UNKNOWN_JUVENILE, 
                'date_of_birth' : birthday,
                'age_uncertainty' : uncertainty,
                'cage' : cage,
                'brood' : brood,
                }
        birdy = Bird(**bird_specs)
        birdy.save()
        
        attf = Activity_Type.objects.get(name='Birth of animal')
        create_text = 'bird was created in database'
        create_bird = Activity(activity_type = attf, activity_content = create_text, \
               bird = birdy, originator = user, start_date = today, end_date = today, \
               severity_grade = Activity.SEVERITY_NONE)
        create_bird.save()
        
    
    #print user.username, firstbirthday, lastbirthday
    comment_text = brood.comment
    if comment_text:
        comment_text += 'birds added by %s with first birthday: %s & last birthday: %s\n'\
                % (str(user.username), str(firstbirthday), str(lastbirthday))
    else:
        comment_text = 'birds added by %s with first birthday: %s & last birthday: %s\n'\
                % (str(user.username), str(firstbirthday), str(lastbirthday))
    brood.comment = comment_text
    brood.save()


def handle_new_couple(male_id_str, female_id_str, type_str, cage, user):
    '''
    '''

    from birdlist.utils.bird import do_animal_transfer

    today = datetime.date.today()

    # find male and female and check whether they are in an experiment 
    # i'm not sure whether the no experiment restriction is too harsh ?
    male = Bird.objects.get(id=int(male_id_str))
#   if Activity.objects.filter(bird=male, activity_type__name='Experiment', end_date=None):
#       return 'You cannot use the male to make a couple because it is still listed to be in an experiment.'
    female = Bird.objects.get(id=int(female_id_str))
#   if Activity.objects.filter(bird=female, activity_type__name='Experiment', end_date=None):
#       return 'You cannot use the female to make a couple because it is still listed to be in an experiment.'

    # they cannot be dead either
    if male.cause_of_exit != None or female.cause_of_exit != None:
        return 'You cannot make this couple: either male or female is not in our colony anymore.'

    # only allow birds with sex MALE/FEMALE for couples
    if male.sex != Bird.SEX_MALE:
        return "The sex of the male bird you\'ve chosen is not \'male\'. Please correct that or use another bird."
    if female.sex != Bird.SEX_FEMALE:
        return "The sex of the female bird you\'ve chosen is not \'female\'. Please correct that or use another bird."


    # using lazy try / except so I don't need to check whether brood & parents exist
    try:
        male_parents = male.brood.get_parents()
        female_parents = female.brood.get_parents()
    
        if (male_parents[0].id == female_parents[0].id) or (male_parents[1].id == female_parents[1].id):
            return "These birds are brothers and sisters - you can't couple them."
    except:
        pass

    # see whether couple already exists -> there can be one or NO entry
    clu = CoupleLookup.objects.filter(father=male, mother=female)

    # add couplelookup and couple otherwise
    if not clu:
        couple = Couple()
        couple.save()
        clu = CoupleLookup(father=male, mother=female, couple=couple)
        clu.save()
    else:
        couple = clu[0].couple

    # see whether there is an open coupling
    coupling = Coupling.objects.filter(couple=couple, separation_date=None)
    if coupling:
        return 'An open Coupling session already exists for this Couple -> HOB!'
    else:
        coupling = Coupling(couple=couple, coupling_date=today, cage=cage, type = int(type_str))
        coupling.save()
        
    do_animal_transfer(male, cage.id, user)
    do_animal_transfer(female, cage.id, user)



def handle_couple_separation(male_cage, female_cage, cage, user, evaluate_breeding, breeder_status):
    '''
    '''
    from birdlist.utils.bird import do_animal_transfer
    
    # force birds to be moved to a non breeding cage
    cage_male = get_object_or_404(Cage, id = male_cage)
    cage_female = get_object_or_404(Cage, id = female_cage)
    if cage_male.function == cage.FUNCTION_BREEDING:
        return 'Please select different cage for male. You can not transfer a bird from a breeding cage into a different breeding cage.'
    
    if cage_female.function == cage.FUNCTION_BREEDING:
        return 'Please select different cage for female. You can not transfer a bird from a breeding cage into a different breeding cage.'
    

    # check that male & female go into correct cages
    cage_check, error_message = cage_male.check_restriction(Bird.SEX_MALE)
    if cage_check == False:
        return "Can not transfer the male into this cage, because the cage has a restriction that is not met: " + error_message

    cage_check, error_message = cage_female.check_restriction(Bird.SEX_FEMALE)
    if cage_check == False:
        return "Can not transfer the female into this cage, because the cage has a restriction that is not met: " + error_message

    # find coupling
    coupling = Coupling.objects.filter(cage=cage, separation_date=None)
    if coupling.count() == 0:
        return 'There is no couple in this cage.'
    elif coupling.count() > 1:
        return 'More than one couple seem to be in this cage. -> HOB'
    else:
        coupling = coupling[0]
    # close coupling
    coupling.separation_date = datetime.date.today()
    # get couplings birds
    male = coupling.couple.get_male()
    female = coupling.couple.get_female()
    if not male or not female:
        return 'Something with the coupling-couple-couplelookup is wrong. -> HOB'
    # move birds to future cages
    coupling.save()
    do_animal_transfer(male, male_cage, user)
    do_animal_transfer(female, female_cage, user)
    
    # flag animals according to breeding status (if given)
    # don't overwrite previously set 'breeder' status!
    if evaluate_breeding == True:
        if female.coupling_status in [Bird.COUPLING_NEVER_USED, Bird.COUPLING_TRY_BREEDING_AGAIN]:
            female.coupling_status = breeder_status
            female.save()
        if male.coupling_status in [Bird.COUPLING_NEVER_USED, Bird.COUPLING_TRY_BREEDING_AGAIN]:
            male.coupling_status = breeder_status
            male.save()


def mother_or_father_need_breeding_evaluation(mother, father, coupling):
    if (mother.coupling_status in [Bird.COUPLING_NEVER_USED, Bird.COUPLING_TRY_BREEDING_AGAIN] \
        or father.coupling_status in [Bird.COUPLING_NEVER_USED, Bird.COUPLING_TRY_BREEDING_AGAIN]) \
        and coupling.type == Coupling.COUPLING_TYPE_BREEDING_COUPLE:
        return True
    else:
        return False


