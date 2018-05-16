'''            SIGNAL RECEIVERS & RECEIVER REGISTRATION                      '''
from django.db.models.signals import pre_save, post_save

from songbird.utils import check_for_changed_model_fields, print_changed_activity_fields
from lablog.models import Experiment
from birdlist.models import Activity, Activity_Type

import datetime


EXPERIMENT_CHANGE_STRING = Activity.EXPERIMENT_CHANGE_STRING

''' receivers '''
def experiment_edit_from_birdlist(sender, **kwargs):
    """signal intercept for pre_save on birdlist.Activity """
    instance = kwargs['instance']
    if instance.activity_type == Activity_Type.objects.get(name = 'Experiment'):
        # existing Activity gets modified
        if instance.id:
            old_entry = Activity.objects.get(id = instance.id)

            # get list of changes.
            mods = check_for_changed_activity_fields(old_entry, instance)
            if mods.__len__() == 0:
                print "No changes applied to 'Experiment'."
                return
            
            # uncomment if you want to see raw list of changed fields
            #
            # print mods
            # print_changed_activity_fields(mods)

            # create activity for changed experiments entry
            log_change_of_experiment(mods, old_entry)
            
            # only do the following, if the experiment already exists in lablog!
            if old_entry.content_object:
                
                # the lablog experiment that is linked to this activity
                experiment = old_entry.content_object
                
                # Check for fields that need to be synced with lablog.
                # activity field and its corresponding lablog field
                fields_to_check = (('activity_content', 'title'), ('start_date', 'start_date'), ('end_date', 'end_date'))
                for i in fields_to_check:
                    activity_name = i[0]
                    if activity_name in mods:
                        # uncomment if you want to debug
                        # print "set in lablog.experiment '" + i[1] + "' to " + str(mods[activity_name][1])
                        experiment.__setattr__(i[1], mods[activity_name][1])
                experiment.save()
            
            else:
                print "No corresponding experiment exists in lablog or experiment has been modified from within the animal list."
        # new Activity got created
        else:
            print "A new experiment got created in the animal list! You can import this experiment in lablog"

    #else:
        #print "Received a non important signal from birdlist regarding a 'non-Experiment' activity."



''' helperfunctions '''    
def check_for_changed_activity_fields(original_object, modified_object):
    return check_for_changed_model_fields(original_object, modified_object, 'birdlist', 'Activity')


def log_change_of_experiment(mods, old_entry):
    a = Activity_Type.objects.filter(name = EXPERIMENT_CHANGE_STRING)
    if a.__len__() == 0:
        a = Activity_Type()
        a.name = EXPERIMENT_CHANGE_STRING
        a.description = "Experiment has been modified"
        a.save()
    else:
        a = a[0]

    
    # don't log cases, where fields were empty and are now filled.
    change_string = build_change_experiment_string(mods)
    if change_string.__len__() == 0:
        return
        
    today = datetime.date.today()
    b = Activity()
    b.bird = old_entry.bird
    b.originator = old_entry.originator
    b.start_date = today
    b.end_date = today
    b.activity_type = a
    b.activity_content = change_string
    b.severity_grade = 0
    b.save()


def build_change_experiment_string(mods):
    ''' 
        see "songbird.utils.print_changed_activity_fields" for similar function
        
    ''' 
    string = ''
    for key in mods.iterkeys():
        # use literal values, if they are present. see 'check_for_changed_model_fields' above
        if mods[key][3]:
            old_value = mods[key][4]
            new_value = mods[key][5]
        else:
            old_value = mods[key][0]
            new_value = mods[key][1]
        
        fieldname = str(mods[key][2])
        # since this function is for experiment changes only, we can replace
        # "activity content" with the proper meaning (so we don't confuse the user)
        if fieldname == 'activity content':
            fieldname = "Experiment info"
        
        # ignore fields that were empty
        if old_value == None:
            continue
            
        string += "'" + fieldname + "'" + " changed from '" +  str(old_value) + "' to '" + str(new_value) + "'" + ".\n"

    return string    


''' unused receivers '''
def experiment_mod_handler(sender, **kwargs):
    """signal intercept for experiment_mod"""
    print "experiment form got called"
    author = kwargs['author']
    title = kwargs['title']
    print author, title


def experiment_save_handler(sender, **kwargs):
    """signal intercept for pre_save on Experiment """
    print "experiment save handler got called"
    
    
        
    
    

