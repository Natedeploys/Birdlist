from django.contrib import admin
from django.contrib.contenttypes import generic

################################################################################
from birdlist.models import ChangeLog

class ChangeLogAdmin(admin.ModelAdmin) :

    # allow to search for experiments by date
    date_hierarchy = 'timestamp'


################################################################################
from django.contrib.contenttypes.models import ContentType
class CommonAdminSettings(admin.ModelAdmin):

    class Meta:
        abstract = True

#   def save_model(self, request, obj, form, change):
#       ''' 
#           overridden save_model - function to always write a 
#           ChangeLog-Entry in addition
#       '''
#       # write everything into the changelog
#       cl = ChangeLog()
#       cl.executing_user = request.user
#       cl.table = ContentType.objects.get(model=obj._meta.module_name)
#       obj.save()
#       cl.object_id = obj.pk

#       fields = obj.get_all_nonrel_fields()
#       #for field in fields :
#       #    cl.mutation += ' %s,' % (obj.__getattribute__(field))
#       cl.mutation += " // %s // " % request.user
#       if change:
#           cl.mutation += 'change // \n \n'
#           cl.mutation += 'the row was changed by %s to \n' % request.user
#       else:
#           cl.mutation += 'creation // \n \n'
#           cl.mutation += 'row creation by %s \n' % request.user

#       cl.mutation += '************************************** \n \n'
#
#       #for field in fields :
#       #    cl.mutation += '%s:\t %s \n' % (field, obj.__getattribute__(field))
#       cl.save()

# does not work properly


################################################################################
from birdlist.models import Bird

class BirdAdmin(CommonAdminSettings) :

    # what fields should be shown in the overview?
    list_display = ('name', 'date_of_birth', 'exit_date', 'species', 'reserved_by')

    # add an additional date filter on the right side
    list_filter = ['species', 'date_of_birth', 'reserved_by'] 
    search_fields = ['name']


################################################################################
from birdlist.models import Activity 

class ActivityAdmin(CommonAdminSettings) :

    date_hierarchy = 'start_date'
    list_display = ('activity_type', 'bird', 'start_date', 'end_date', 'originator')
    list_filter = ['activity_type', 'start_date', 'originator']     

    exclude = ('originator', )

    def save_model(self, request, obj, form, change) :
        if not change :
            obj.originator = request.user
        obj.save()


## inline model to show up in the experiment database
class ActivityAdminInline(generic.GenericTabularInline):
    model = Activity

################################################################################
from birdlist.models import Activity_Type

class Activity_TypeAdmin(CommonAdminSettings):
    
    list_display = ('name', 'in_use',)


################################################################################
from birdlist.models import Cage

class CageAdmin(CommonAdminSettings):
    list_filter = ['room'] 
    save_as = True

################################################################################
from birdlist.models import LabRoom

class LabRoomAdmin(CommonAdminSettings):
    list_filter = ['room_number'] 

################################################################################
from birdlist.models import Animal_Experiment_Licence

class Animal_Experiment_LicenceAdmin(CommonAdminSettings):
    date_hierarchy = 'valid_from'


from birdlist.models import Couple, Coupling, Brood, CoupleLookup
class CoupleAdmin(CommonAdminSettings):
    model = Couple

class CouplingAdmin(CommonAdminSettings):
    model = Coupling

class BroodAdmin(CommonAdminSettings):
    model = Brood

class CoupleLookupAdmin(CommonAdminSettings):
    model = CoupleLookup

################################################################################
# now register all admin interfaces

admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(Couple, CoupleAdmin)
admin.site.register(Coupling, CouplingAdmin)
admin.site.register(Brood, BroodAdmin)
admin.site.register(CoupleLookup, CoupleLookupAdmin)
admin.site.register(Bird, BirdAdmin)
admin.site.register(Cage, CageAdmin)
admin.site.register(LabRoom, LabRoomAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Activity_Type, Activity_TypeAdmin)
admin.site.register(Animal_Experiment_Licence, Animal_Experiment_LicenceAdmin)

