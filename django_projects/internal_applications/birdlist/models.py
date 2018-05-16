from django.db import models
from django.contrib.auth.models import User
from tagging_autocomplete.models import TagAutocompleteField

import datetime

# this dummy class seems to be needed by django evolution
# i created this type one time, it did not fully work
# so it was removed but it still seems to be searched for ..
class UniquifyField(models.NullBooleanField):

    pass


################################################################################
# changelog for any changes in the birdlist
################################################################################
from django.contrib.contenttypes.models import ContentType

class ChangeLog(models.Model) :
    timestamp   = models.DateTimeField(auto_now_add=True)
    executing_user = models.ForeignKey(User)
    table = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    mutation = models.TextField()

    class Meta :
        verbose_name = 'Change Log'
        verbose_name_plural = 'Change Log Entries'

    def __unicode__(self) :
        return u'%s  -  %s  -  %s' % (self.timestamp, self.table, self.executing_user)
    
################################################################################
# base class to be inherited on all other classes in this app 
################################################################################
from string import split
class CommonStuff(models.Model):

    # function to return non relational field/attributes of a model
    def get_all_nonrel_fields(self) :
        fields = self._meta.get_all_field_names()
        #fields.remove(split(split(str(self._meta.get_all_related_objects()[0]))[1], ':')[1])
        return fields

    def save(self, *args, **kwargs):
        #print "Before save"
        super(CommonStuff, self).save(*args, **kwargs) # Call the "real" save() method

        # we want to write the ChangeLog Entry once an entry is saved
        # we need:
        # - access to request.user
        # - the object module_name
        # - object.pk

        # print dir(self)

        ''' 
            overridden save_model - function to always write a 
            ChangeLog-Entry in addition
        '''

        '''
        # write everything into the changelog
        cl = ChangeLog()
        cl.executing_user = request.user
        cl.table = ContentType.objects.get(model=obj._meta.module_name)
        obj.save()
        cl.object_id = obj.pk

        fields = obj.get_all_nonrel_fields()
        #for field in fields :
        #    cl.mutation += ' %s,' % (obj.__getattribute__(field))
        cl.mutation += " // %s // " % request.user
        if change:
            cl.mutation += 'change // \n \n'
            cl.mutation += 'the row was changed by %s to \n' % request.user
        else:
            cl.mutation += 'creation // \n \n'
            cl.mutation += 'row creation by %s \n' % request.user

        cl.mutation += '************************************** \n \n'
 
        #for field in fields :
        #    cl.mutation += '%s:\t %s \n' % (field, obj.__getattribute__(field))
        cl.save()

        '''
        #print "After save"


    class Meta:
        abstract = True


################################################################################
class LabRoom(CommonStuff):

    room_number     = models.CharField(max_length=255)
    description     = models.CharField(max_length=255, unique=True)

    in_use          = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s - %s' % (self.room_number, self.description)


################################################################################
# birdlist classes
################################################################################

class CageManager(models.Manager):

    def get_empty_cages(self, function='nofunction', room=None):
        '''
        function: use Cage.FUNCTION_XXX
        room: use room instance

        cause FUNCTION_BREEDING=0 we have to use this somewhat stupid kwarg

        !! returns a list, not a queryset !!
        '''
        cages = Cage.objects.all()
        if function != 'nofunction':
            cages = cages.filter(function=function)
        if room:
            cages = cages.filter(room=room)
        
        empty_cages_list = []
        for cage in cages:
            if cage.bird_set.count() == 0:
                empty_cages_list.append(cage)

        return empty_cages_list


class Cage(CommonStuff):

    name            = models.CharField(max_length=255, unique=True)
    room            = models.ForeignKey(LabRoom)
    max_occupancy   = models.PositiveIntegerField()

    FUNCTION_BREEDING = 0
    FUNCTION_LONGTERMSTORAGE = 1
    FUNCTION_TEMPORARYSTORAGE = 2
    FUNCTION_ISOLATIONRECORDINGS = 3
    FUNCTION_ISOLATIONDEVELOPMENTAL = 4
    FUNCTION_RECOVERY = 5
    FUNCTION_CHRONICEXPERIMENT = 6
    FUNCTION_QUARANTINE = 7
    FUNCTION_BREEDINGBREAK = 8
    FUNCTION_SOCIAL = 9
    FUNCTION_DISPOSAL = 10
    FUNCTION_MISSING = 11
    FUNCTION_NOTUSEDANYMORE = 12

    FUNCTION_CHOICES = (
            (FUNCTION_BREEDING, 'breeding'),
            (FUNCTION_LONGTERMSTORAGE, 'long term storage'),
            (FUNCTION_TEMPORARYSTORAGE, 'temporary storage'),
            (FUNCTION_ISOLATIONRECORDINGS, 'isolation (recordings)'),
            (FUNCTION_ISOLATIONDEVELOPMENTAL, 'isolation (developmental)'),
            (FUNCTION_RECOVERY, 'recovery'),
            (FUNCTION_CHRONICEXPERIMENT, 'chronic experiment'),
            (FUNCTION_QUARANTINE, 'quarantine'),
            (FUNCTION_BREEDINGBREAK, 'breeding break'),
            (FUNCTION_SOCIAL, 'social'),
            (FUNCTION_DISPOSAL, 'disposal'),
            (FUNCTION_MISSING, 'missing'),
            (FUNCTION_NOTUSEDANYMORE, 'not used anymore'),
    )

    function      = models.PositiveIntegerField(choices = FUNCTION_CHOICES, default=0)
    
    
    RESTRICTION_MALE = 1
    RESTRICTION_FEMALE = 2
    
    RESTRICTION_CHOICES = (
            (RESTRICTION_MALE, 'male animals only'),
            (RESTRICTION_FEMALE, 'female animals only'),
    )
    
    restriction = models.PositiveIntegerField(choices = RESTRICTION_CHOICES, blank = True, null = True)
    
    # add the custom manager
    objects = CageManager()

    def __unicode__(self):
        if self.restriction:
            return u'%s - %s (%s); (%s)' % (self.name, self.get_function_display(), self.get_restriction_display(), self.room)
        else:
            return u'%s - %s; (%s)' % (self.name, self.get_function_display(), self.room)


    def check_restriction(self, restriction_check = None):
        check_ok = True
        error_message = ''
        if restriction_check == None:
            return check_ok, error_message

        if self.restriction:
            if self.restriction == Cage.RESTRICTION_MALE and (restriction_check != Bird.SEX_MALE):
                error_message = "Sex of animal does not match cage restriction."
                check_ok = False
            
            if self.restriction == Cage.RESTRICTION_FEMALE and (restriction_check != Bird.SEX_FEMALE):
                error_message = "Sex of animal does not match cage restriction."
                check_ok = False
        
        return check_ok, error_message
        

    def occupancy(self):
        return Bird.objects.filter(cage__id = self.id).filter(missing_since=None).__len__()
        
    def has_couple(self):
        # find coupling with our cage id and where the separation date is empty
        if Coupling.objects.filter(cage__id = self.id, separation_date = None).__len__() >= 1:
            # print "has couple inside"
            return True
        else:
            #print "no current couple"        
            return False


    def has_foster_couple(self):
        # find coupling with our cage id and where the separation date is empty
        if Coupling.objects.filter(cage__id = self.id, separation_date = None, type = Coupling.COUPLING_TYPE_FOSTER_COUPLE).__len__() >= 1:
            return True
        else:
            return False


    def couple_comment(self):
        # find coupling with our cage id and where the separation date is empty
        couplings = Coupling.objects.filter(cage__id = self.id, separation_date = None)
        try:
            return couplings.get().comment
        except:
            return ''

    @models.permalink
    def get_absolute_url(self):
        return ('cage_overview', [self.name])

    @models.permalink
    def get_addjuvs_url(self):
        if self.function == self.FUNCTION_BREEDING:
            return ('add_juveniles_to_cage', [self.name])
        else:
            return "."

    @models.permalink
    def get_separation_url(self):
        if self.has_couple:
            return ('separate_couple', [self.name])
        else:
            return "."

    @models.permalink
    def get_addcouple_url(self):
        return ('add_couple_to_cage', [self.name])
        

################################################################################

class Couple(CommonStuff):
    comment  = models.TextField(blank = True, null = True)

    def __unicode__(self):
        return u'%s' % (self.get_bird_names())

    def get_bird_names(self):
        '''
        returns a string containing the names of male and female
        '''
        try:
            couplelookup = CoupleLookup.objects.get(couple=self.pk)
            return u'm: %s, f: %s' % (couplelookup.father, couplelookup.mother)
        except:
            return 'this couple has no birds - please report to database responsible'

    def get_male(self):
        '''
        return the bird instance of the male
        '''
        try:
            couplelookup = CoupleLookup.objects.get(couple=self.pk)
            return couplelookup.father
        except:
            return

    def get_female(self):
        '''
        return the bird instance of the female
        '''
        try:
            couplelookup = CoupleLookup.objects.get(couple=self.pk)
            return couplelookup.mother
        except:
            return
            
    def get_partner(self, sex):
        '''
        return the right partner given the "sex"
        '''
        if sex == Bird.SEX_MALE:
            return self.get_female()
        elif sex == Bird.SEX_FEMALE:
            return self.get_male()
            
    def get_female_and_male(self):
        '''
        return mother and father objects
        '''      
        try:
            couplelookup = CoupleLookup.objects.get(couple=self.pk)
            return couplelookup.mother, couplelookup.father
        except:
            return None, None

class Coupling(CommonStuff):
    couple          = models.ForeignKey(Couple)
    cage            = models.ForeignKey(Cage)
    coupling_date   = models.DateField(auto_now_add = False)
    separation_date = models.DateField(auto_now_add = False, blank = True, null = True)
    comment         = models.TextField(blank = True, null = True)

    COUPLING_TYPE_BREEDING_COUPLE = 0
    COUPLING_TYPE_FOSTER_COUPLE = 1
    COUPLING_TYPE_CHOICES = (
            (COUPLING_TYPE_BREEDING_COUPLE, 'normal breeding couple'),
            (COUPLING_TYPE_FOSTER_COUPLE, 'foster parents'),
    )

    type = models.PositiveIntegerField(choices = COUPLING_TYPE_CHOICES, default=COUPLING_TYPE_BREEDING_COUPLE)

    # we set the separation threshold here centrally
    SEPARATION_THRESHOLD = datetime.timedelta(60)

    class Meta: 
        verbose_name = 'Coupling'
        verbose_name_plural = 'Coupling'

    def __unicode__(self):
        return u'%s : from %s till %s' % (self.get_couple(), self.coupling_date, self.separation_date)

    def get_couple(self):
        '''
        a lookup function that returns a string containing the names of male and female
        of the corresponding couple
        '''
        try:
            return u'm: %s, f: %s' % (self.couple.get_male(), self.couple.get_female())
        except:
            return 'bought, given, unknown, ..'

    def get_number_of_broods(self):
        '''
        '''
        return Brood.objects.filter(coupling=self).count()

    def get_last_brood(self):
        '''
        '''
        # order_by get_broods_birthday does not work -> order by id should
        # give us the same result unless a brood would be registered after the
        # next was born. which should never happen
        broods = Brood.objects.filter(coupling=self).order_by('id').reverse()
        if broods:
            last_brood = broods[0]
        else:
            last_brood = None

        return last_brood

    def is_to_be_separated(self):
        '''
        is this couple to be separated?
        '''

        # get last brood
        last_brood = self.get_last_brood()
        # today's date
        today = datetime.date.today()
        # number of animals in cage
        nbr_animals_in_cage = self.cage.bird_set.all().count()

        # breeding couples
        if self.type == Coupling.COUPLING_TYPE_BREEDING_COUPLE:
            # if last brood is more than 60 days away
            if last_brood and (today - last_brood.get_broods_birthday() >= self.SEPARATION_THRESHOLD):
                return True
            # if there is no brood at all since 60 days
            if not last_brood and (today - self.coupling_date >= self.SEPARATION_THRESHOLD):
                return True
            # if there are 3 generations and no juveniles in the breeding cage, ie. there are only 2 birds inside
            if self.brood_set.all().count() >= 3 and nbr_animals_in_cage == 2:
                return True
            else:
                return False

        # foster couples - separate if couple is by itself 
        elif self.type == Coupling.COUPLING_TYPE_FOSTER_COUPLE:
            if nbr_animals_in_cage <= 2:
                return True
            else:
                return False

    def nest_has_to_be_removed(self):
        '''
        nest has to be removed if
        - three generations were born
        - birds of couple were marked with coupling status 'do not couple'
        
        generally this has to be done as soon as the most recent generation left the nest.
        '''

        # check only necessary for breeding couples.
        if self.type == Coupling.COUPLING_TYPE_BREEDING_COUPLE:
            if self.separation_date == None:

                if self.brood_set.all().count() >= 3:
                    return True

                female, male = self.couple.get_female_and_male()
                if female.coupling_status ==  Bird.COUPLING_DO_NOT_COUPLE or male.coupling_status == Bird.COUPLING_DO_NOT_COUPLE:
                    return True

            return False
        
        # non-breeding couples.
        else:
            return False


class BroodManager(models.Manager):
    '''
    '''
    def get_brood_within_broodrange(self, coupling, date):
        '''
        find a brood that belongs to a given coupling and 
        whose birthday is within brood_range
        '''
        possible_broods = self.filter(coupling=coupling)
        for brood in possible_broods:
            if brood.get_is_within_range(date):
                return brood


class Brood(CommonStuff):
    '''
    a brood is a bunch of birds that belong together. either they are 
    brothers and sister that hatched within 10 days (1 generation).
    in that case their date_of_birth is the day the oldest bird in that generation
    was born, for all of them. age_uncertainty is the amount of days between the youngest
    and the oldest bird.
    it can also be a group of birds that were bought together.
    '''
    # the number of days within which in the case of home grown 
    # birds birthdays have to fall to assign them to the same brood
    BROOD_RANGE = 10
    
    ORIGIN_BREEDING = 1
    ORIGIN_EXTERNAL = 2
    ORIGIN_UNKNOWN = 3
    ORIGIN_FOSTER = 4

    ORIGIN_CHOICES = (
            (ORIGIN_BREEDING, 'lab own breeding'),
            (ORIGIN_EXTERNAL, 'external / bought'),
            (ORIGIN_UNKNOWN, 'unknown'),
            (ORIGIN_FOSTER, 'own breeding - foster parents'),
    )

    origin   = models.IntegerField(choices = ORIGIN_CHOICES)
    coupling = models.ForeignKey(Coupling, blank=True, null=True)
    comment  = models.TextField(blank = True, null = True)

    # add the custom BroodManager
    objects = BroodManager()


    def __unicode__(self):
        return self.create_unicode_string()


    def get_parents(self):
        '''
        returns the parent birds, like (male, female) or a message about the
        birds origin else
        '''
        if (self.origin == self.ORIGIN_BREEDING) or (self.origin == self.ORIGIN_FOSTER):
            try:
                return self.coupling.couple.get_male(), self.coupling.couple.get_female()
            except:
                return 'problem with couple look up and name retrieval in Brood.get_parents()'
        else:
            return 'no parents registered: brood.origin = %s' % self.origin

    
    def get_broods_birthday(self):
        '''
        '''
        if self.ORIGIN_BREEDING:
            birdy = Bird.objects.filter(brood=self.pk)
            if birdy:
                # all birds must have same birthday -> simply take first
                birdy = birdy[0]
                if birdy.date_of_birth:
                    return birdy.date_of_birth
        return


    def get_is_within_range(self, date):
        '''
        is this brood within BROOD_RANGE days from brood_birthday
        '''
        birthday = self.get_broods_birthday()
        max_range = self.get_broods_birthday() + datetime.timedelta(self.BROOD_RANGE)
        return date <= max_range and date >= birthday


    def create_unicode_string(self):
        '''
        '''
        try:
            parents = self.get_parents()
            parent1 = parents[0]
            parent2 = parents[1]
            info = (parent1, parent2, str(self.get_broods_birthday()))
        except:
            info = ''
            pass

        if self.origin == self.ORIGIN_BREEDING and self.coupling:
            return u'%s & %s : m&f - %s' % info
        elif self.origin == self.ORIGIN_EXTERNAL:
            return u'origin external: %s' % self.comment
        elif self.origin == self.ORIGIN_FOSTER:
            return u'foster animal raised by %s & %s : m&f - %s' % info
        else:
            return u'unknown type'

################################################################################
from django.core.validators import validate_slug

class Bird(CommonStuff):
    '''
    The model for a database bird.

    Note:
    -> date_of_birth and age_uncertainty are stored with every bird individually, rather than with the brood
    -> there are functions that return mother and father of the bird if possible
    
    TODO:
    we do not enforce uniqueness of names of living birds at all right now
    -> for data consistency this has to be done though!!!
       maybe this could be of help: http://djangosnippets.org/snippets/1830/
    '''
    
    JUVENILE_PREFIX = 'J'
    

    name_help_text = 'Birdnames have to consist of alphabetic letters, numbers, hyphens or underscores.'
    name        = models.CharField(max_length = 255, validators=[validate_slug], help_text=name_help_text)
    
    SEX_UNKNOWN_JUVENILE = 'u'
    SEX_UNKNOWN_NOT_VISIBLE = 'v'
    SEX_MALE = 'm'
    SEX_FEMALE = 'f'

    SEX_CHOICES     =   (
                            (SEX_UNKNOWN_JUVENILE, 'unknown - juvenile'),
                            (SEX_UNKNOWN_NOT_VISIBLE, 'unknown - not visible'),
                            (SEX_MALE, 'male'),
                            (SEX_FEMALE, 'female'),
                        )

    sex             = models.CharField(max_length = 1, choices = SEX_CHOICES)


    SPECIES_ZEBRAFINCH = 'ZF'
    SPECIES_BENGALESEFINCH = 'BF'

    SPECIES_CHOICES =   (
                            (SPECIES_ZEBRAFINCH, 'zebra finch'),
                            (SPECIES_BENGALESEFINCH, 'bengalese finch'), 
                        )
    
    date_of_birth = models.DateField(auto_now_add = False, blank = True, null = True)

    AGE_UNCERTAINTY_CHOICES = (
            (0, 'zero days'),
            (-1, 'one day'),
            (-2, 'two days'),
            (-3, 'three days'),
            (-4, 'four days'),
            (-5, 'five days'),
            (-6, 'six days'),
            (-7, 'seven days'),
            (-8, 'more than seven days'),
    )

    age_uncertainty = models.IntegerField(choices = AGE_UNCERTAINTY_CHOICES)
    
    species         = models.CharField(max_length = 10, choices = SPECIES_CHOICES)
    brood           = models.ForeignKey(Brood, blank = True, null = True)

    cage        = models.ForeignKey(Cage)

    reserved_until  = models.DateField(blank = True, null = True)
    reserved_by    = models.ForeignKey(User, blank = True, null = True)

    missing_since   = models.DateField(blank = True, null = True)
    
    COUPLING_NEVER_USED = 0
    COUPLING_DO_NOT_COUPLE = 1
    COUPLING_BREEDER = 2
    COUPLING_TRY_BREEDING_AGAIN = 3
    COUPLING_CHOICES = (
            (COUPLING_NEVER_USED, 'never used for breeding'),
            (COUPLING_DO_NOT_COUPLE, 'do not couple'),
            (COUPLING_BREEDER, 'good breeder'),
            (COUPLING_TRY_BREEDING_AGAIN, 'semi-ok breeder'),
    )
    
    coupling_status = models.PositiveIntegerField(choices = COUPLING_CHOICES, default=COUPLING_NEVER_USED)

    comment         = models.TextField(blank = True, null = True)

    exit_date       = models.DateField(blank=True, null=True)

    # name_unique declares whether a birds name has to be unique
    # generally birds alive in our breeding colony have to be unique 
    # the NullBooleanField has three possible entries: Null, False, True
    # birds to be unique will need entry yes, birds whose name can be used
    # MULTIPLE times HAVE TO USE NULL, False is not to be used
    # TODO : enforce not using False
    name_unique     = models.NullBooleanField(default=True, null=True) 
    
    # don't use magic numbers!
    # see also: http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/

    EXIT_NONE = 0
    EXIT_SLEEP = 1
    EXIT_SURGERY = 2
    EXIT_PERISHED = 3
    EXIT_NONEXPERIMENTAL = 4
    EXIT_GIVENAWAY = 5
    EXIT_MISSING = 6

    CAUSE_OF_EXIT_CHOICES = (
            (EXIT_NONE, '-----'), 
            (EXIT_SLEEP, 'end of experiment (chronic / acute sleep)'), 
            (EXIT_SURGERY, 'end of experiment (surgery / under anesthesia)'),
            (EXIT_PERISHED, 'perished'), 
            (EXIT_NONEXPERIMENTAL, 'not experimental'), 
            (EXIT_GIVENAWAY, 'given away'),
            (EXIT_MISSING, 'missing'),
    )

    cause_of_exit   = models.PositiveIntegerField(choices = CAUSE_OF_EXIT_CHOICES, blank = True, null = True, verbose_name="Reason for removal")
    tags = TagAutocompleteField()

    name.alphabetic_filter = True


    class Meta:
        ordering            = ['name', ]
        unique_together = ('name', 'name_unique')


    def __unicode__(self):
        return u'%s' % (self.name)


    @models.permalink
    def get_absolute_url(self):
        return ('bird_overview', [str(self.id)])


    @models.permalink
    def get_edit_url(self):
        return ('bird_edit', [str(self.id)])


    # function to return the age of the bird
    def get_phd(self, relative_to_day = None, return_empty = None):

        # only calculate the age if the field is set - for old birds or
        # outbreeders there might be no birthday
        if self.date_of_birth:

            if relative_to_day:
                age = relative_to_day - self.date_of_birth
            else:
                age = datetime.date.today() - self.date_of_birth

            age = age.days.__str__()
            age = age # + ' phd' printing 'phd' in all forms is a space issue 
        else:
            if return_empty == True:
                age = None
            else:
                age = '?'

        return age


    def get_father(self):
        try:
            if self.brood.origin == Brood.ORIGIN_BREEDING:
                    return self.brood.coupling.couple.get_male()
        except:
            return


    def get_sex_display(self):
        ''' if sex is unknown, show only the 'unknown', otherwise show the short
            sex names (f, m) '''
        try:
            if self.sex in (Bird.SEX_UNKNOWN_NOT_VISIBLE, Bird.SEX_UNKNOWN_JUVENILE):
                return 'unknown'
            else:
                return self.sex
        except:
            return self.sex


    def get_mother(self):
        try:
            if self.brood.origin == Brood.ORIGIN_BREEDING:
                    return self.brood.coupling.couple.get_female()
        except:
            return


    def get_mother_and_father(self):
        try:
            if self.brood.origin == Brood.ORIGIN_BREEDING:
                # slow way
                #return self.brood.coupling.couple.get_female_and_male()

                # fast way
                couplelookup = CoupleLookup.objects.get(couple__coupling__brood__bird = self)
                return couplelookup.mother, couplelookup.father
        except:
            return None, None


    def get_couple_ids(self):
        ''' get all couple IDs that this bird was part of '''
    
        couples = []
        if self.sex not in (Bird.SEX_MALE, Bird.SEX_FEMALE):
            return couples

        if self.sex == Bird.SEX_MALE:
            couples = self.father_set.all().values_list('couple', flat = True)
        else:
            couples = self.mother_set.all().values_list('couple', flat = True)

        return couples


    def get_couplings(self):
        ''' get all couplings that this bird was involved in '''
        
        couple_ids = self.get_couple_ids()
        couples = Couple.objects.filter(id__in = couple_ids)
        
        # for all couples, find all couplings
        couplinglists = []
        for clui in couples:
            couplinglists.append(clui.coupling_set.all().select_related('couple').order_by('coupling_date'))

        # this code is doing the same, but doesn't group couplings that belong
        # to the same couple
        #Coupling.objects.filter(couple__id__in = couple_ids).select_related('couple').order_by('coupling_date')

        return couplinglists


    def get_offspring(self):
        ''' returns all offspring of current bird 
            this function takes roughly 3ms 
        '''
        
        couple_ids = self.get_couple_ids()
        
        # the following code is doing the same, but is ~ 10% slower
        #from django.db.models import Q
        #couple_ids = CoupleLookup.objects.filter(Q(Q(father = self.id) | Q(mother = self.id))).values_list('couple', flat = True)
        
        # return only birds that were part of a 'breeding couple'
        return Bird.objects.filter(brood__coupling__couple__in = couple_ids, brood__origin = Brood.ORIGIN_BREEDING)


    def get_mates_string(self):
        '''
        returns a string with the mates of a bird, 
        how successful they were and when they were separated.
        '''

        mates = ''

        # all couplings that this bird was involved in
        couplinglists = self.get_couplings()
        if couplinglists == []:
            return mates
        
        # now we have a list of lists of couplings for a bird / couple
        for couplinglist in couplinglists:
            # now we go through the couples
            mates += couplinglist[0].couple.get_partner(self.sex).name
            # and count its offspring over several couplings
            offcount = 0
            for coupling in couplinglist:
                offcount += coupling.brood_set.all().count()
            # put offspring and separation_date of last coupling into string
            mates += '('+str(offcount)+' - ' + str(coupling.separation_date)+'), '
        mates = mates[:-2]
        
        return mates


    def get_mates_dict(self):

        mates = []
        last_separation = None

        # all couplings that this bird was involved in
        couplinglists = self.get_couplings()
        if couplinglists == []:
            return { 'mates': mates, 'last_separation': last_separation }

        # now we have a list of lists of couplings for a bird / couple
        for couplinglist in couplinglists:
            # now we go through the couples
            # and count its offspring over several couplings
            broodcount = 0
            juvcount = 0
            partner = couplinglist[0].couple.get_partner(self.sex)
            for coupling in couplinglist:
                broods = coupling.brood_set.all()
                broodcount += broods.__len__()
                for brood in broods:
                    juvcount += brood.bird_set.all().__len__()


            coupling_list_len = couplinglist.__len__()

            # put info into dict
            mate_dict = {
                    'bird': partner,
                    'AvgNoBroods': float(broodcount)/float(coupling_list_len),
                    'AvgNoJuvs': float(juvcount)/float(coupling_list_len),
                    'last_separation': coupling.separation_date, 
                    'NoCouplings': coupling_list_len, 
                    }

            if last_separation:
                if last_separation < coupling.separation_date:
                    last_separation = coupling.separation_date
            else:
                last_separation = coupling.separation_date

            # append dict to mates list
            mates.append(mate_dict)

        return { 'mates': mates, 'last_separation': last_separation } 


    def build_family_tree(self):

        family = []
        mother, father = self.get_mother_and_father()

        # all couplings that this bird was involved in
        couplinglists = self.get_couplings()
        if couplinglists == []:
            return { 'family': family, 'mother': mother, 'father': father, }

        # now we have a list of lists of couplings for a bird / couple
        for couplinglist in couplinglists:
            partner = couplinglist[0].couple.get_partner(self.sex)
            partner_mother, partner_father = partner.get_mother_and_father()
            
            for coupling in couplinglist:
                offspring_this_coupling = []
                broods = coupling.brood_set.all()
                
                for brood in broods:
                    offspring_this_coupling = brood.bird_set.all()
                    
                    offspring_this_coupling_with_offspring = []
                    for j in offspring_this_coupling:
                        this_offspring = j.get_offspring()
                        has_offspring = False
                        
                        if this_offspring.__len__() > 0:
                            has_offspring = True
                            
                        offspring_this_coupling_with_offspring.append([j, has_offspring])

                    # put info into dict
                    generation_dict = {
                            'partner': partner, 
                            'partner_father': partner_father, 
                            'partner_mother': partner_mother, 
                            'coupling_date': coupling.coupling_date,
                            'separation_date': coupling.separation_date, 
                            'offspring_with_offspring': offspring_this_coupling_with_offspring, 
                            }

                    # append dict
                    family.append(generation_dict)

        return { 'family': family, 'mother': mother, 'father': father, } 


    def is_breeding(self):
        # current couples
        from birdlist.utils.bird import find_birds_currently_breeding
        males, females = find_birds_currently_breeding()            
        if self.id in males or self.id in females:
            return True
        else:
            return False            
    

    def is_juvenile_to_be_transferred(self):
        from birdlist.utils.bird import get_juveniles
        lower_datethreshold = datetime.date.today()-datetime.timedelta(60)
        juveniles = get_juveniles().filter(date_of_birth__lte=lower_datethreshold).filter(cage__function=Cage.FUNCTION_BREEDING)
        if self in juveniles:
            return True
        else:
            return False
        
    def get_current_partner(self):
        try:
            couple_in_cage = Coupling.objects.get(cage__name = self.cage.name, separation_date = None)
            partner = couple_in_cage.couple.get_partner(self.sex)
            return partner
        except:
            return None

################################################################################
class CoupleLookup(CommonStuff):
    couple = models.ForeignKey(Couple)
    father = models.ForeignKey(Bird, related_name = 'father_set')
    mother = models.ForeignKey(Bird, related_name = 'mother_set')

    class Meta:
        unique_together = ('couple', 'father', 'mother')
        verbose_name = 'Couple LookUp'
        verbose_name_plural = 'Couple LookUps'

    def __unicode__(self):
        return u'male: %s; female: %s' % (self.father, self.mother)


################################################################################
class Animal_Experiment_Licence(CommonStuff):

    title           = models.CharField(max_length=255)
    description     = models.TextField()
    valid_from      = models.DateField()
    valid_until     = models.DateField()
       
    class Meta:
        verbose_name = 'Animal Experiment Licence'
        verbose_name_plural = 'Animal Experiment Licences'

    def __unicode__(self):
        return u'%s; valid from %s until %s' % (self.title, self.valid_from, self.valid_until)


################################################################################
class Activity_Type(CommonStuff):

    name            = models.CharField(max_length=255, unique=True)
    description     = models.TextField()
    in_use          = models.BooleanField(default=True)
    creation_date   = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Type'
        verbose_name_plural = 'Activity Types'
        
    def __unicode__(self):
        return u'%s' % (self.name)        


################################################################################
from django.contrib.contenttypes import generic

class Activity(CommonStuff):

    bird                = models.ForeignKey(Bird)
    originator          = models.ForeignKey(User)
    start_date          = models.DateField()
    end_date            = models.DateField(blank=True, null=True)
    activity_type       = models.ForeignKey(Activity_Type)
    
    activity_content_help = 'Please provide a log entry for your activity.'
    activity_content    = models.TextField(blank=True, null=True, help_text=activity_content_help)

    SEVERITY_NONE = 0
    SEVERITY_ONE = 1
    SEVERITY_TWO = 2
    SEVERITY_THREE = 3    

    SEVERITY_GRADE_CHOICES = (
            (SEVERITY_NONE, 'no pain, no stress (SG 0)'),
            (SEVERITY_ONE, 'little and short pain: everything under anesthesia / behavioural experiments, bird isolated from friends. (SG 1)'),
            (SEVERITY_TWO, 'chronic / acute sleep experiments (SG 2)'),
            (SEVERITY_THREE, 'animal perishes during experiment or is exposed to long lasting pain (SG 3)'),
    )
    severity_grade      = models.PositiveIntegerField(choices = SEVERITY_GRADE_CHOICES)
    animal_experiment_licence = models.ForeignKey(Animal_Experiment_Licence, blank=True, null=True)

    content_type        = models.ForeignKey(ContentType, null=True, blank=True)
    object_id           = models.PositiveIntegerField(null=True, blank=True)
    content_object      = generic.GenericForeignKey("content_type", "object_id")
    
    # timestamps to track creation and modifications of activities
    timestamp_created = models.DateTimeField(auto_now_add=True)
    timestamp_modified = models.DateTimeField(auto_now=True)


    CAGE_TRANSFER_STRING = 'Cage Transfer'
    RESERVATION_STRING = 'Reservation'
    RENAMING_STRING = 'Renaming'
    EXPERIMENT_STRING = 'Experiment'
    HEALTH_STATUS_STRING = 'Health Status'
    EXPERIMENT_CHANGE_STRING = 'Experiment Change'
    BIRTH_ANIMAL_STRING = 'Birth of animal'    

    # not editable activity types
    NOTEDITABLE = (CAGE_TRANSFER_STRING, RESERVATION_STRING, RENAMING_STRING, EXPERIMENT_CHANGE_STRING, BIRTH_ANIMAL_STRING)
    # activity types for which we need to check if originator == current user
    CHECKFORPERMISSIONS = (EXPERIMENT_STRING, )
    # all activity types for which we want to show details. They need to be in 
    # sync with activity_detail.html
    ALLDETAIL = NOTEDITABLE + CHECKFORPERMISSIONS

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
    
    def __unicode__(self) :
        return u'%s - %s' % (self.bird, self.activity_type)


    @models.permalink
    def get_absolute_url(self):
        return ('activity_detail', (), {'activity_id': self.id})
        
    @models.permalink
    def get_edit_url(self):
        if self.activity_type.name in self.NOTEDITABLE:
            # same code as above in 'get_absolute_url'. We can not call 
            # 'get_absolute_url' here, because the urls are all effed up.
            return ('activity_detail', (), {'activity_id': self.id})
        else:
            return ('activity_edit', (), {'activity_id': self.id})

    def get_bird_name(self) :
        return u'%s' % self.bird
        
    def get_activity_content_pretty(self):
        if self.activity_type.name == 'Experiment':
            long_string = '\n----------------------------------------\n'
            str_found = self.activity_content.find(long_string)
            if str_found == -1:
                return self.activity_content
            else:
                content_length = self.activity_content.__len__()
                long_string_length = long_string.__len__()

                # if there's a comment, then separate exp text from comment
                replace_by = ': '
                
                # no comment
                if str_found + long_string_length == content_length:
                    replace_by = ''
                    
                import re
                experiment_name = re.sub(long_string, replace_by, self.activity_content)  
                return experiment_name                          

        else:
            return self.activity_content        

#EOF
