from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime, AdminTextareaWidget
from django.db import models
from django import forms
from django.core.exceptions import ValidationError

from birdlist.forms.birdlist_common import BirdlistForm
from birdlist.models import Activity, Bird, Activity_Type, Animal_Experiment_Licence

import datetime

class ActivityForm(BirdlistForm):

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        if 'start_date' in self.fields:
            self.fields['start_date'].widget = AdminDateWidget()
            self.fields['start_date'].help_text = 'The start date cannot not be in the future.' 
        if 'end_date' in self.fields:
            self.fields['end_date'].widget = AdminDateWidget()
            self.fields['end_date'].help_text = 'The end date cannot not be in the future. Please update the db as soon as the experiment is over.' 
        if 'originator' in self.fields:
            self.fields['originator'].widget = forms.HiddenInput()
        if 'bird' in self.fields:
            self.fields['bird'].widget = forms.HiddenInput()
        if 'activity_type' in self.fields:
            self.fields['activity_type'].widget = forms.HiddenInput()

    class Meta:
        model = Activity 
        exclude = ('content_type', 'object_id',)

    def clean_start_date(self, *args, **kwargs):

        if self.cleaned_data['start_date']:
            if self.cleaned_data['start_date'] > datetime.date.today():
                raise ValidationError('The start date cannot be in the future.')

        return self.cleaned_data['start_date']
        
    def clean_end_date(self, *args, **kwargs):
        
        if self.cleaned_data['end_date']:
            if self.cleaned_data['end_date'] > datetime.date.today():
                raise ValidationError('The end date cannot be in the future. Please update the database as soon as the experiment is over.')

        return self.cleaned_data['end_date']


#   def clean(self, *args, **kwargs):
#       '''
#       '''
#       super(ActivityForm, self).clean(*args, **kwargs)
#       # TODO: make sure dates are not in the future
#       # DON'T DO 'pass' here! this will crash the form validation!!
#       
#       cleaned_data = self.cleaned_data
#       return cleaned_data


class ActivityFormExperiment(ActivityForm):
    def __init__(self, *args, **kwargs):
        super(ActivityFormExperiment, self).__init__(*args, **kwargs)
        self.fields['activity_content'].required = True
        self.fields['activity_content'].help_text = "Please provide an experiment name and description."
        self.fields['activity_content'].label = "Experiment name and description"
        self.fields['animal_experiment_licence'].required = True
        self.fields['animal_experiment_licence'].help_text = "You need to specify the licence which applies to your experiment."
        self.fields['end_date'].widget = forms.HiddenInput()

    def clean_animal_experiment_licence(self, *args, **kwargs):
        # check whether animal experiment licence is valid for experiment (start) date
        lic = None
        if self.cleaned_data.has_key('animal_experiment_licence'):
            lic = self.cleaned_data['animal_experiment_licence']
        
        sd = None
        if self.cleaned_data.has_key('start_date'):
            sd = self.cleaned_data['start_date']
        
        # 'start_date' will be 'None' if it's in the future.
        if lic == None or sd == None:
            return

        if not (sd >= lic.valid_from and sd <= lic.valid_until):
                raise ValidationError('This licence is only valid from %s until %s.' % (str(lic.valid_from), str(lic.valid_until)))

        return self.cleaned_data['animal_experiment_licence']


class ActivityFormHealthStatus(ActivityForm):
    def __init__(self, *args, **kwargs):
        super(ActivityFormHealthStatus, self).__init__(*args, **kwargs)
        self.fields['activity_content'].required = True
        self.fields['activity_content'].help_text = "Please provide information about the birds health status."
        self.fields['activity_content'].label = "Health status description"
        self.fields['severity_grade'].widget = forms.HiddenInput()
        self.fields['severity_grade'].initial = Activity.SEVERITY_NONE        

    class Meta:
        model = Activity 
        exclude = ('content_type', 'object_id', 'animal_experiment_licence' )


from autocomplete.widgets import AutoCompleteWidget
class ActivityFormAddExperimentFromLablog(BirdlistForm):
    def __init__(self, *args, **kwargs):
        super(ActivityFormAddExperimentFromLablog, self).__init__(*args, **kwargs)
        self.fields['bird'].required = False
        self.fields['severity_grade'].required = False
        self.fields['bird'].widget = AutoCompleteWidget('birdname')
        
        self.fields['originator'].widget = forms.HiddenInput()
        self.fields['start_date'].widget = forms.HiddenInput()
        self.fields['end_date'].widget = forms.HiddenInput()
        self.fields['activity_content'].widget = forms.HiddenInput()                

        # prefill activity type
        a = Activity_Type.objects.get(name = 'experiment')
        self.fields['activity_type'].widget = forms.HiddenInput()
        self.fields['activity_type'].initial = a.id


from django.contrib.auth.models import User 
class ActivityUserlist(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all().exclude(id__in = (1, 18)).order_by('username'), empty_label=None)

class ActivityLicenceList(forms.Form):
    licence = forms.ModelChoiceField(queryset=Animal_Experiment_Licence.objects.all(), empty_label=None)


''' close experiments '''
class ActivityFormExperimentClose(BirdlistForm):
    checkout_animal_from_database = forms.BooleanField()
    def __init__(self, *args, **kwargs):
        super(ActivityFormExperimentClose, self).__init__(*args, **kwargs)
        self.fields['activity_content'].required = True
        self.fields['activity_content'].help_text = "Please provide an experiment name and description."
        self.fields['activity_content'].label = "Experiment name and description"
        self.fields['end_date'].widget = AdminDateWidget()
        self.fields['end_date'].required = True
        self.fields['checkout_animal_from_database'].help_text = "Is this experiment fatal? Should we try to checkout the animal from the database?"
        self.fields['checkout_animal_from_database'].required = False

    class Meta:
        model = Activity 
        exclude = ('content_type', 'object_id', 'animal_experiment_licence', 
                    'severity_grade', 'start_date', 'bird', 
                    'originator', 'activity_type')

    def clean_end_date(self, *args, **kwargs):
        if self.cleaned_data['end_date']:
            if self.cleaned_data['end_date'] > datetime.date.today():
                raise ValidationError('The end date cannot be in the future. Please update the database as soon as the experiment is over.')

        return self.cleaned_data['end_date']


class ActivityFormExperimentCloseHideCheckoutOption(ActivityFormExperimentClose):
    def __init__(self, *args, **kwargs):
        super(ActivityFormExperimentCloseHideCheckoutOption, self).__init__(*args, **kwargs)
        self.fields['checkout_animal_from_database'].widget = forms.HiddenInput()


class ActivityFormExperimentCheckIfSongRecorded(forms.Form):
    choices = (
            ('none', '---'),
            (1, 'no song recording'),
            (2, 'song recording'),
    )
    exp_type = forms.TypedChoiceField(choices = choices)
    
    def __init__(self, *args, **kwargs):
        super(ActivityFormExperimentCheckIfSongRecorded, self).__init__(*args, **kwargs)
        self.fields['exp_type'].required = True
        self.fields['exp_type'].label = "Experiment Type"
        self.fields['exp_type'].help_text = "Did your experiment involve recording of song?"
        
    def clean_exp_type(self, *args, **kwargs):

        if self.cleaned_data['exp_type']:
            if self.cleaned_data['exp_type'] == 'none':
                raise ValidationError('Please tell us whether you have recorded song or not. Thanks!')

        return self.cleaned_data['exp_type']        

    
class ActivityFormExperimentCheckNbrSyls(forms.Form):
    choices = (
            (0, '0 - bird did not sing'),
            (1, '1 syllable'),
            (2, '2 syllables'),
            (3, '3 syllables'),
            (4, '4 syllables'),
            (5, '5 syllables'),
            (6, '6 syllables'),
            (7, '7 syllables'),
            (8, '8 syllables'),
            (9, '9 syllables'),
            (10, '10 syllables'),
    )
    nbr_syls = forms.TypedChoiceField(choices = choices)    
    def __init__(self, *args, **kwargs):
        super(ActivityFormExperimentCheckNbrSyls, self).__init__(*args, **kwargs)
        self.fields['nbr_syls'].required = True
        self.fields['nbr_syls'].label = "Number of syllables in motif"
        self.fields['nbr_syls'].help_text = "How many syllables did your bird sing?"


