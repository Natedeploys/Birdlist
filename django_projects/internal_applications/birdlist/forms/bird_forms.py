from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime, AdminTextareaWidget
from django.template.defaultfilters import slugify
from birdlist.models import Bird, Activity, Cage 
from django import forms
import time

from songbird.widgets.widgets import SelectWithPop, MultipleSelectWithPop

from birdlist.forms.birdlist_common import BirdlistForm

class BirdFormBase(BirdlistForm):

    def __init__(self, *args, **kwargs):
        super(BirdFormBase, self).__init__(*args, **kwargs)
        if 'date_of_birth' in self.fields:
            self.fields['date_of_birth'].widget = AdminDateWidget()
        if 'reserved_until' in self.fields:
            self.fields['reserved_until'].widget = AdminDateWidget()
        if 'exit_date' in self.fields:
            self.fields['exit_date'].widget = AdminDateWidget()
        if 'missing_since' in self.fields:
            self.fields['missing_since'].widget = AdminDateWidget()
        if 'name_unique' in self.fields:
            self.fields['name_unique'].widget = forms.HiddenInput()
        if 'reserved_by' in self.fields:
            self.fields['reserved_by'].widget = forms.HiddenInput()
        if 'reserved_by' in self.fields:
            self.fields['reserved_by'].widget = forms.HiddenInput()

    class Meta:
        model = Bird 


class BirdFormEdit(BirdFormBase):

    def __init__(self, *args, **kwargs):
        super(BirdFormEdit, self).__init__(*args, **kwargs)
        if 'missing_since' in self.fields:
            self.fields['missing_since'].widget = forms.HiddenInput()
        if 'exit_date' in self.fields:
            self.fields['exit_date'].widget = forms.HiddenInput()
            
        # changing widget to HiddenInput because the cage field is always empty 
        # in case user changes the cage. But users should use 'transfer bird' 
        # action instead anyway     
        self.fields['cage'].widget = forms.HiddenInput()      
        #self.fields['cage'].queryset = Cage.objects.exclude(function=Cage.FUNCTION_NOTUSEDANYMORE)
        #self.fields['cage'].help_text = "If you change the Cage here you also create a \'Cage Transfer Activity\' dated for today."
        
        # we have a 'reserve bird' action for this.        
        self.fields['reserved_until'].widget = forms.HiddenInput()
        
        # we have a 'CheckoutAnimalFromColony' action for this
        self.fields['cause_of_exit'].widget = forms.HiddenInput()


    class Meta:
        # we have to declare the model again cause only one class Meta 
        # instance is called at class initialization
        model = Bird
        # never exclude the name_unique field, otherwise validation of 
        # uniqueness will fail -> field is hidden in parent class and won't
        # display anyways
        exclude = ('date_of_birth', 'age_uncertainty', 'brood', )

    ''' crashes form validation with cryptic error
    # don't leave an empty clean function
    def clean_sex(self):
        data = self.cleaned_data
        # if the bird is more than 60 days old, you have to decide for a sex
        if data['sex'] == Bird.SEX_UNKNOWN_JUVENILE and int(self.instance.get_phd()) > 60:
            raise forms.ValidationError("Sex cannot be unknown at this age. If you cannot determine the sex, set it to \'unknown - not visible\'.")
        return data
    ''' 
