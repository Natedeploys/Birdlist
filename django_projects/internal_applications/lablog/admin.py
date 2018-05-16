from django.contrib import admin
from birdlist.admin import ActivityAdminInline

################################################################################
# "raw" admin classes - not using inheritance from custom super class
################################################################################


################################################################################
# custom super class used by all models below
################################################################################

# new idea based on: http://www.djangosnippets.org/snippets/1054/
# see also: http://www.b-list.org/weblog/2008/dec/24/admin/

class CommonAdminSettings(admin.ModelAdmin):

    class Meta:
        abstract = True
        
    # show save bar on top because some forms might be very long        
    # save_on_top = True
    
    # add save_as button
    save_as = True

    # django 1.0
    #exclude = ['author']

    # django 1.0.2
    exclude = ('author', )

    # show only author's own entries as long as you don't have more permissions
    def queryset(self, request):
        qs = super(CommonAdminSettings, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(author = request.user)
            

    # validate form, set user if not super user
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()
        
    # check class-level permission, because they are true by default
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(CommonAdminSettings, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.author.id:
            return False
        return True

    # make sure to only show entries owned by the current user in the "add / change" page
    def get_form(self, request, obj=None):

        form = super(CommonAdminSettings, self).get_form(request, obj)
        
        if not request.user.is_superuser:
            fieldnames = form.base_fields.keyOrder
            for y in fieldnames:
                if y == "project":
                    form.base_fields['project'].queryset = Project.objects.filter(author = request.user)
                elif y == "experiment":
                    form.base_fields['experiment'].queryset = Experiment.objects.filter(author = request.user)
                elif y == "event_type":
                    form.base_fields['event_type'].queryset = Event_Type.objects.filter(author = request.user);


        return form

    has_delete_permission = has_change_permission


################################################################################
# a class for INLINES so we don't need to exclude the 'author' field everytime
################################################################################
class CommonAdminInlineSettings(admin.TabularInline):

    class Meta:
        abstract = True

    # inline does not inherit the exclude values so we need to exclude the 
    exclude = ['author']


################################################################################
# all model classes using the super class.
################################################################################
from lablog.models import Experiment
class ExperimentInline(CommonAdminInlineSettings):
    model = Experiment
    extra = 1
    list_display = ('name', 'birth_day')


################################################################################
from lablog.models import Project
class ProjectAdmin(CommonAdminSettings):

    # inlines = [ExperimentInline]

    # allow to search for experiments by date
    date_hierarchy = 'start_date'

    # what fields should be shown in the overview?
    list_display = ('title', 'start_date', 'author')

    # search for exact title of experiment
    search_fields = ['name']

    # add an additional date filter on the right side
    list_filter = ['start_date', 'author', 'title',] 
    
    # prepopulate the slug
    prepopulated_fields = {'slug': ('title', 'start_date')}

################################################################################
class ExperimentAdmin(CommonAdminSettings):

    # allow to search for experiments by date
    date_hierarchy = 'start_date'

    # what fields should be shown in the overview?
    list_display = ('title', 'start_date', 'author')

    # search for exact title of experiment
    search_fields = ['bird']

    # add an additional date filter on the right side
    list_filter = ['start_date', 'author',] 

    # prepopulate the slug
    prepopulated_fields = {'slug': ('title', 'start_date')}

    # this breaks our nice "author - hide" functionality.
    #
    # mandatory fields first    
    # fieldsets = (
    #   (None, {
    #        'fields': ('author', 'title', 'bird', 'start_date', 'project')
    #    }),
    #    ('Advanced options', {
    #        'classes': ('collapse',),
    #        'fields': ('plan', 'comment', 'protocol', 'data_path', 'media_path', 'end_date')
    #    }),
    #)


    inlines = [
        ActivityAdminInline,
    ]


################################################################################
from lablog.models import Protocol
class ProtocolAdmin(CommonAdminSettings):

    # allow to search for experiments by date
    date_hierarchy = 'timestamp'

    # what fields should be shown in the overview?
    list_display = ('title', 'valid_until', 'timestamp', 'author')

    # search for exact title of experiment
    search_fields = ['title']

    # add an additional date filter on the right side
    list_filter = ['timestamp', 'author',] 

    # prepopulate the slug
    prepopulated_fields = {'slug': ('title', )}

################################################################################
from lablog.models import Note 
class NoteAdmin(CommonAdminSettings):

    # allow to search for experiments by date
    date_hierarchy = 'date'

    # what fields should be shown in the overview?
    list_display = ('date', 'occasion', 'entry')

    # search for exact title of experiment
    search_fields = ['occasion']

    # add an additional date filter on the right side
    list_filter = ['date', 'author',] 

################################################################################
from lablog.models import Event_Type
class Event_TypeAdmin(CommonAdminSettings):

    # what fields should be shown in the overview?
    list_display = ('event_type', 'text_field')
    
    # add an additional date filter on the right side
    list_filter = ['author',]     


################################################################################
from lablog.models import Event
class EventAdmin(CommonAdminSettings):

    # allow to search for experiments by date
    date_hierarchy = 'timestamp'

    # what fields should be shown in the overview?
    list_display = ('date', 'time', 'event_type', 'text_field', 'experiment', 'timestamp', 'author')

    # add an additional date filter on the right side
    list_filter = ['author', 'date', 'experiment',] 

    

################################################################################
# now register all admin interfaces
################################################################################

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Event_Type, Event_TypeAdmin)
admin.site.register(Event, EventAdmin)
# EOF

