from django.db import models
from django.contrib.auth.models import User
from tagging_autocomplete.models import TagAutocompleteField


################################################################################
# super class used in custom models

class CommonSettings(models.Model):
    """
    A meta class to inherit common settings to all database classes.    
    """
    class Meta:
        abstract = True


################################################################################
# database classes - inheriting from CommonSettings

class Project(CommonSettings):
    """
    Container for experiments etc. with common goal.
    """
    author      = models.ForeignKey(User)
    title       = models.CharField(max_length=255, help_text = "Please provide a title for your project.")
    slug        = models.SlugField(help_text = "Please provide a short unique identifier for this project")
    start_date  = models.DateField(help_text = "When did you start with this project?")
    description = models.TextField(help_text = "What's the purpose of this project?")
    end_date    = models.DateField(blank=True, null=True)
    data_path   = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        unique_together = ("author", "slug")

    def __unicode__(self) :
        return u'%s' % (self.title)


class Protocol(CommonSettings):
    """
    Protocol. Standard procedure to which one can refer to in order to abbreviate the lab journal.
    """
    author      = models.ForeignKey(User)
    timestamp   = models.DateTimeField(auto_now_add=True)
    title       = models.CharField(max_length=255)
    slug        = models.SlugField()
    description = models.TextField()
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("author", "slug") 

    def __unicode__(self) :
        return u'%s' % (self.title)


class Note(CommonSettings):
    """
    Note to Project.
    """
    author      = models.ForeignKey(User)
    occasion    = models.CharField(max_length=255)
    date        = models.DateTimeField()
    entry       = models.TextField()
    project     = models.ForeignKey(Project)

    SCHEDULE_PAST = 1
    SCHEDULE_FUTURE = 2
    SCHEDULE_PARTIAL = 3

    SCHEDULE_CHOICES = (
            (SCHEDULE_PAST, 'Note in the past (default)'), 
            (SCHEDULE_FUTURE, 'Future note: ToDo'),
            (SCHEDULE_PARTIAL, 'Future note: partially started'),
    )

    schedule    = models.PositiveIntegerField(choices = SCHEDULE_CHOICES, verbose_name="Schedule Note", blank = False, help_text = "Is this a past or a future note?")


    def __unicode__(self):
        return self.occasion


from django.contrib.contenttypes import generic
from birdlist.models import Activity

class Experiment(CommonSettings):
    """
    An Experiment.
    """
    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    slug = models.SlugField(help_text = "Please provide a short unique identifier for this experiment (like 'my_super_duper_experiment')")
    start_date = models.DateField()

    project = models.ForeignKey(Project, help_text = "Every experiment must be linked to a project.")
    protocol = models.ManyToManyField(Protocol, blank = True, null = True)
    
    plan = models.TextField(
                blank = True, 
                null = True, 
                verbose_name = "Plan / Description", 
                help_text = "What do you plan to do in this experiment?",
                )

    DATA_NONE = 1
    DATA_NOT_POSTPROCESSED = 2
    DATA_PARTIALLY_POSTPROCESSED = 3
    DATA_POSTPROCESSED = 4

    DATA_CHOICES = (
            (DATA_NONE, 'No useful data recorded.'), 
            (DATA_NOT_POSTPROCESSED, 'Not postprocessed'),
            (DATA_PARTIALLY_POSTPROCESSED, 'Partially postprocessed'), 
            (DATA_POSTPROCESSED, 'Finished postprocessing'), 
    )

    data = models.PositiveIntegerField(
                    choices = DATA_CHOICES, 
                    blank = True, 
                    null = True, 
                    help_text = "Did you record data? Did you postprocess it?",
                    )


    end_date = models.DateField(blank = True, null = True)

    
    from songbird.settings import LABLOG_MEDIA
    data_path   = models.CharField(
                    max_length = 1000, 
                    blank = True, 
                    null = True, 
                    help_text = "Data files folder, relative to '" + LABLOG_MEDIA + "' - currently not used.",
                    )
                                    
    media_path  = models.CharField(
                    max_length = 1000, 
                    blank = True, 
                    null = True, 
                    help_text = "Media files folder, relative to '" + LABLOG_MEDIA + "'.",
                    )
                    
    comment = models.TextField(
                    blank = True, 
                    null = True, 
                    help_text = "Here you have space for additional notes, comments, reports, etc ...",
                    )

    bird = generic.GenericRelation(Activity)
    

    class Meta:
        unique_together = ("author", "slug")   
    
    
    def __unicode__(self):
        return self.title

        
    def can_be_merged_with_animallist(self):
        from lablog.views.experiment.experiment_main import ANIMAL_DATABASE_KICKOFFDATE
        PRE_DB_KICKOFF = None
        if self.start_date < ANIMAL_DATABASE_KICKOFFDATE:
            PRE_DB_KICKOFF = True
        
        # is an activity associated with this experiment?
        activity_associated_with_experiment = None
        try:
            activity_associated_with_experiment = self.bird.get()
        except:
            # this will fail if there is no association
            pass
            
        if PRE_DB_KICKOFF and activity_associated_with_experiment == None:
            return True
        else:
            return False


class Event_Type(CommonSettings):
    """
    Category for LabLog Event.
    """
    author          = models.ForeignKey(User)
    event_type      = models.CharField(max_length=100, verbose_name="Event Type", help_text = "What is the your event type called?")
    text_field      = models.CharField(max_length=255, verbose_name="Header / Input Grammar", help_text = "default: 'None', use '|' to separate fields. ")
    flag_meaning    = models.CharField(max_length=255, verbose_name="Definition for On / Off", help_text = "default: 'None', use '|' to separate fields.")
    flag_color      = models.CharField(blank=True, null=True, max_length=255, verbose_name="On / Off color", help_text = "Color used to highlight the on / off states. Default: '', use '|' to separate fields.")
    display_order   = models.IntegerField(help_text = "How important is this event type? 1 == very important and therefore this event type will be shown at the beginning of the list.")
    hierarchy_order = models.IntegerField(blank=True, null=True, help_text = "Not used, ignore?")

    class Meta:
        verbose_name        = 'Event Type'
        verbose_name_plural = 'Event Types'
        unique_together     = ("author", "event_type")
        ordering            = ['display_order', 'event_type']
        
    def __unicode__(self):
        return u'%s' % (self.event_type)


class Event(CommonSettings):
    """
    A log event is a constituent of an experiment.
    """
    author      = models.ForeignKey(User)
    timestamp   = models.DateTimeField(auto_now_add=True)
    event_type  = models.ForeignKey(Event_Type, verbose_name="Event type")
    text_field  = models.TextField(blank=True, null=True, max_length=2048, help_text = "what did you do?", verbose_name="Event")
    flag_box    = models.BooleanField(verbose_name="On / Off", help_text = "Please be careful with correctly setting this flag. Leave unckecked for 'On', check for 'Off'")
    time        = models.TimeField()
    date        = models.DateField()
    experiment  = models.ForeignKey(Experiment)

    SCHEDULE_PAST = 1
    SCHEDULE_FUTURE = 2
    SCHEDULE_PARTIAL = 3

    SCHEDULE_CHOICES = (
            (SCHEDULE_PAST, 'Event in the past (default)'), 
            (SCHEDULE_FUTURE, 'Future event: ToDo'),
            (SCHEDULE_PARTIAL, 'Future event: partially started'),
    )

    schedule        = models.PositiveIntegerField(choices = SCHEDULE_CHOICES, verbose_name="Schedule Event", blank = False, help_text = "Is this a past or a future event?")

    tags = TagAutocompleteField()

    def __unicode__(self):
        return u"%s" % (self.timestamp)




'''            SIGNAL RECEIVERS & RECEIVER REGISTRATION                      '''
from django.db.models.signals import pre_save, post_save, pre_delete
from lablog.signals import experiment_mod
from birdlist.models import Activity, Activity_Type
from lablog.utils.birdlist_sync_through_activity import experiment_edit_from_birdlist, experiment_mod_handler, experiment_save_handler
from lablog.utils.experiment import delete_experiment_signal_receiver

''' register receivers '''
# will be called automatically
pre_save.connect(experiment_edit_from_birdlist, sender = Activity, dispatch_uid = "fromBirdlist")
pre_delete.connect(delete_experiment_signal_receiver, sender = Experiment)


''' disabled receivers '''
# you need to manually call this one
# experiment_mod.connect(experiment_mod_handler, sender=Experiment, dispatch_uid="my_unique_identifier")

# will be called automatically
# pre_save.connect(experiment_save_handler, sender=Experiment, dispatch_uid="asgdasdfasdfasdf")

