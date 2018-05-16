'''
functions that help maintain a consistent database
'''
import datetime
from django.contrib.auth.models import User

from birdlist.models import Bird, Cage, Activity_Type, Activity


def clean_up_db(save=False):
    '''
    collection of cleanup functions
    '''
    status_message = ''
    status_message += remove_expired_reservations(save=save)
    status_message += '\n' + missing_birds_cleanup(save=save)

    return status_message


def missing_birds_cleanup(save=False):
    '''
    finds all birds that are registered to be missing
    if a bird is missing for more than a year bird is set to 'OutOfColony'
    exit_date is one year after it went missing
    cause_of_exit = EXIT_MISSING
    missing_since remains -> allows statistics about missing birds

    -> add comment explaining process
    '''

    status_message = '\n\nCHECKOUT MISSING BIRDS --------------------------\n'

    # get all birds that have a missing_since date
    missing_birds =  Bird.objects.exclude(missing_since=None).filter(exit_date=None)
    missing_checkout = False
    
    for bird in missing_birds:
        if datetime.date.today() - bird.missing_since >= datetime.timedelta(days=365):
            missing_checkout = True
            bird.exit_date = bird.missing_since + datetime.timedelta(days=365)
            bird.cause_of_exit = Bird.EXIT_MISSING
            bird.cage = Cage.objects.get(name='OutOfColony')
            if bird.comment:
                bird.comment = bird.comment + '\n\nBird was checked out of database one year after it went missing.'
            else:
                bird.comment = 'Bird was checked out of database one year after it went missing.'
            
            status_message += bird.name + ' was checked out of database one year after it went missing.\n'

            if save:
               bird.save()

    if not missing_checkout:
        status_message += 'No bird is missing for more than one year.\n' 

    return status_message


from birdlist.utils.bird import do_cancel_reservation
def remove_expired_reservations(save = False):
    ''' why is save optional? not saving the modified datasets doesn't make much 
        sense, does it?
    '''

    status_message = 'REVOKE EXPIRED RESERVATIONS ---------------\n'    
    activity_text = '\nReservation was automatically revoked after it expired.'
    
    reserved_birds = Bird.objects.exclude(reserved_until = None)
    today = datetime.date.today()
    revoked_reservation = False

    for bird in reserved_birds:
        if bird.reserved_until < today:
            revoked_reservation = True
            status_message += '\nremoved reservation from bird - ' + bird.name + ' - '
            status_message += 'bird was reserved by ' + bird.reserved_by.username + ' until: ' + str(bird.reserved_until)
            do_cancel_reservation(bird, activity_text)

    if not revoked_reservation:
        status_message += 'There is no bird with an expired reservation.'

    return status_message


