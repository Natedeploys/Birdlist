from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
import django.forms as forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime, AdminTextareaWidget
from lablog.models import Experiment, Protocol, Project, Event_Type, Event, Note
import time

from songbird.widgets.widgets import SelectWithPop, MultipleSelectWithPop

################################################################################
# Form models
##

class LablogForm(ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super(LablogForm, self).__init__(*args, **kwargs)
        self.user = user


class LablogFormHideAuthor(LablogForm):
    def __init__(self, *args, **kwargs):
        super(LablogFormHideAuthor, self).__init__(*args, **kwargs)
        # hide the author field, don't use exclude in the meta class because we use unique_together for author & event_type
        self.fields['author'].widget = forms.HiddenInput()


class EventFormBasic(LablogForm):
    def __init__(self, *args, **kwargs):
        super(EventFormBasic, self).__init__(*args, **kwargs)
        current_time = time.localtime()
        self.fields['date'].initial = time.strftime("%Y-%m-%d", current_time)
        self.fields['time'].initial = time.strftime("%H:%M:%S", current_time)
        self.fields['flag_box'].initial = False
        self.fields['text_field'].initial = ""
        self.fields['schedule'].initial = Event.SCHEDULE_PAST
        self.fields['event_type'].queryset = Event_Type.objects.filter(author__username__exact=self.user)

    class Meta:
        model = Event
        exclude = ('author', )


class EventFormQuick(EventFormBasic):
    def __init__(self, *args, **kwargs):
        super(EventFormQuick, self).__init__(*args, **kwargs)
        self.fields['date'].widget = forms.HiddenInput()
        self.fields['time'].widget = forms.HiddenInput()
        self.fields['experiment'].widget = forms.HiddenInput()
        self.fields['text_field'].widget.attrs['rows'] = 2
        self.fields['text_field'].widget.attrs['cols'] = 27

class EventFormMinimal(EventFormBasic):
    def __init__(self, *args, **kwargs):
        super(EventFormMinimal, self).__init__(*args, **kwargs)
        self.fields['date'].widget = forms.HiddenInput()
        self.fields['time'].widget = forms.HiddenInput()
        self.fields['experiment'].widget = forms.HiddenInput()
        self.fields['text_field'].widget = forms.HiddenInput()
        self.fields['flag_box'].widget = forms.HiddenInput()
        self.fields['schedule'].widget = forms.HiddenInput()


class EventForm(EventFormBasic):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # since we override the widget, we need to set the queryset again"
        self.fields['event_type'].widget = SelectWithPop(self.user)
        self.fields['event_type'].queryset = Event_Type.objects.filter(author__username__exact=self.user)
        self.fields['experiment'].widget = SelectWithPop(self.user)
        self.fields['experiment'].queryset = Experiment.objects.filter(author__username__exact=self.user)
        self.fields['date'].widget = AdminDateWidget()
        self.fields['time'].widget = AdminTimeWidget()


class NoteForm(LablogForm):
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['occasion'].widget.attrs['size'] = 100
        self.fields['project'].widget = SelectWithPop(self.user)
        self.fields['project'].queryset = Project.objects.filter(author__username__exact=self.user)
        # set the text field size to a reasonable default
        self.fields['entry'].widget.attrs['rows'] = 20
        self.fields['entry'].widget.attrs['cols'] = 50  
        #
        self.fields['date'].widget = AdminSplitDateTime();
        self.fields['schedule'].initial = Note.SCHEDULE_PAST

    class Meta:
        model = Note
        exclude = ('author',)  
        
        
class ProjectForm(LablogFormHideAuthor):
    start_date = forms.DateField(widget = AdminDateWidget)
    end_date = forms.DateField(widget = AdminDateWidget, required=False)
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['size'] = 100
        self.fields['slug'].widget.attrs['size'] = 100
    
    class Meta:
        model = Project
        
''' disabled for the moment, because we have no way to distinguish between edits 
    of an old object and creating a new object         
    def clean(self):
        cleaned_data = self.cleaned_data
        slug = cleaned_data.get("slug")
        author = cleaned_data.get("author")

        if slug and Project.objects.filter(slug=slug, author = author).__len__() == 1:
            msg = u"This slug is already in use - please choose a different one."
            self._errors["slug"] = self.error_class([msg])
            # forms.ValidateError should be used but it doesn't show up in our form.
            #raise forms.ValidationError(msg)

        # Always return the full collection of cleaned data.
        return cleaned_data          
'''        
        
class ProtocolForm(LablogFormHideAuthor):
    valid_until = forms.DateField(widget = AdminDateWidget, required=False)
    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['size'] = 100
        self.fields['slug'].widget.attrs['size'] = 100
        self.fields['description'].widget.attrs['rows'] = 20
        self.fields['description'].widget.attrs['cols'] = 72
        
    class Meta:
        model = Protocol

''' disabled for the moment, because we have no way to distinguish between edits 
    of an old object and creating a new object 
    def clean(self):
        cleaned_data = self.cleaned_data
        slug = cleaned_data.get("slug")
        author = cleaned_data.get("author")

        if slug and Protocol.objects.filter(slug=slug, author = author).__len__() == 1:
            msg = u"This slug is already in use - please choose a different one."
            self._errors["slug"] = self.error_class([msg])
            # forms.ValidateError should be used but it doesn't show up in our form.
            #raise forms.ValidationError(msg)

        # Always return the full collection of cleaned data.
        return cleaned_data 
'''        

#add new event-type pop-up
class EventTypeForm(LablogFormHideAuthor):
    def __init__(self, *args, **kwargs):
        super(EventTypeForm, self).__init__(*args, **kwargs)
        self.fields['text_field'].initial = "None"
        self.fields['flag_meaning'].initial = "None"
        self.fields['display_order'].initial = 1

    class Meta:
        model = Event_Type

''' disabled for the moment, because we have no way to distinguish between edits 
    of an old object and creating a new object 
        
    def clean(self):
        cleaned_data = self.cleaned_data
        event_type = cleaned_data.get("event_type")
        author = cleaned_data.get("author")

        if event_type and Event_Type.objects.filter(event_type=event_type, author = author).__len__() == 1:
            msg = u"This event type already exists - please choose a different name."
            self._errors["event_type"] = self.error_class([msg])
            # forms.ValidateError should be used but it doesn't show up in our form.
            #raise forms.ValidationError(msg)

        # Always return the full collection of cleaned data.
        return cleaned_data        
'''

class ExperimentForm(LablogFormHideAuthor):
    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['size'] = 100
        self.fields['slug'].widget.attrs['size'] = 100
        self.fields['project'].widget = SelectWithPop(self.user)
        self.fields['project'].queryset = Project.objects.filter(author__username__exact=self.user)
        self.fields['protocol'].widget = MultipleSelectWithPop(self.user)
        self.fields['protocol'].queryset = Protocol.objects.filter(author__username__exact=self.user)

        current_time = time.localtime()
        self.fields['start_date'].widget = AdminDateWidget()
        self.fields['start_date'].initial = time.strftime("%Y-%m-%d", current_time)
        self.fields['end_date'].widget = AdminDateWidget()

        
        # render path fiels as Textareas, because the CharFields are just too short.
        self.fields['data_path'].widget = forms.Textarea()
        self.fields['media_path'].widget = forms.Textarea()
        self.fields['data_path'].widget.attrs['cols'] = 60
        self.fields['data_path'].widget.attrs['rows'] = 5
        self.fields['media_path'].widget.attrs['cols'] = 60
        self.fields['media_path'].widget.attrs['rows'] = 5
    
    class Meta:
        model = Experiment
        fields = ['author', 'title', 'slug', 'start_date', 'project', 'protocol', 
        'plan', 'data', 'end_date', 'data_path', 'media_path', 'comment', ]
        
''' disabled for the moment, because we have no way to distinguish between edits 
    of an old object and creating a new object 
    
    def clean(self):
        cleaned_data = self.cleaned_data
        slug = cleaned_data.get("slug")
        author = cleaned_data.get("author")

        if slug and Experiment.objects.filter(slug=slug, author = author).__len__() == 1:
            msg = u"This slug is already in use - please choose a different one."
            self._errors["slug"] = self.error_class([msg])
            # forms.ValidateError should be used but it doesn't show up in our form.
            #raise forms.ValidationError(msg)

        # Always return the full collection of cleaned data.
        return cleaned_data        
'''   

class ExperimentFormBasic(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExperimentFormBasic, self).__init__(*args, **kwargs)
        
        self.fields['author'].widget = forms.HiddenInput()
        
        self.fields['title'].widget.attrs['size'] = 100
        self.fields['slug'].widget.attrs['size'] = 100

        current_time = time.localtime()
        self.fields['start_date'].widget = AdminDateWidget()
        self.fields['start_date'].initial = time.strftime("%Y-%m-%d", current_time)
        self.fields['end_date'].widget = AdminDateWidget()

        
        # render path fiels as Textareas, because the CharFields are just too short.
        self.fields['data_path'].widget = forms.Textarea()
        self.fields['media_path'].widget = forms.Textarea()
        self.fields['data_path'].widget.attrs['cols'] = 60
        self.fields['data_path'].widget.attrs['rows'] = 5
        self.fields['media_path'].widget.attrs['cols'] = 60
        self.fields['media_path'].widget.attrs['rows'] = 5
    
    class Meta:
        model = Experiment
        fields = ['author', 'title', 'slug', 'start_date', 'project', 'protocol', 
        'plan', 'data', 'end_date', 'data_path', 'media_path', 'comment', ]

     

from django.template.defaultfilters import slugify
from birdlist.models import Activity
class ExperimentFormAddFromAnimalList(ExperimentForm):
    activity_id = forms.CharField(widget = forms.HiddenInput())
    def __init__(self, activity_id = None, *args, **kwargs):
        super(ExperimentFormAddFromAnimalList, self).__init__(*args, **kwargs)
        self.activity_id = activity_id
        
        # semi fake values
        self.fields['activity_id'].initial = activity_id        
        self.fields['title'].initial = 'FromActivity'
        
        default_title = Activity.objects.get(id = activity_id).activity_content
        self.fields['plan'].initial = default_title
        self.fields['slug'].initial = slugify(default_title)
        
        # hide these fields because we use the settings from the animal list
        self.fields['start_date'].widget = forms.HiddenInput()
        self.fields['title'].widget = forms.HiddenInput()


from tagging.forms import TagField
from tagging_autocomplete.widgets import TagAutocomplete
class TagEvent(forms.Form):
    tag = TagField(widget=TagAutocomplete())
    def __init__(self, *args, **kwargs):
        super(TagEvent, self).__init__(*args, **kwargs)

