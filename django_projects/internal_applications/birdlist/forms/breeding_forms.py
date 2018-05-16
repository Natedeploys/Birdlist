from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime, AdminTextareaWidget
from django.db import models
from django import forms

from birdlist.forms.birdlist_common import BirdlistForm
from birdlist.models import Activity, Bird, Activity_Type, Brood, Coupling

import datetime

class AddJuvenilesForm(forms.Form):
    '''
    '''
    FirstBirthday = forms.DateField(widget=AdminDateWidget())
    LastBirthday = forms.DateField(widget=AdminDateWidget())
    NumberOfJuvenilesToAdd = forms.IntegerField(min_value=1, max_value=10)

    def __init__(self, *args, **kwargs):
        super(AddJuvenilesForm, self).__init__(*args, **kwargs)
        self.fields['FirstBirthday'].required = True
        self.fields['LastBirthday'].required = True
        self.fields['NumberOfJuvenilesToAdd'].required = True

        self.fields['FirstBirthday'].label = "First Day"
        self.fields['FirstBirthday'].help_text = "The first day on which a NEWLY BORN YOU WANT TO ADD TO THE BIRDLIST was found."

        self.fields['LastBirthday'].label = "Last Day"
        self.fields['LastBirthday'].help_text = "The last day on which a NEWLY BORN YOU WANT TO ADD TO THE BIRDLIST was found."

        self.fields['NumberOfJuvenilesToAdd'].label = "# Newborns"
        self.fields['NumberOfJuvenilesToAdd'].help_text = "The number of NEWLY BORNS YOU WANT TO ADD TO THE BIRDLIST."


    def clean(self, *args, **kwargs):
        '''
        '''
        data = self.cleaned_data

        # check that FirstBirthday and LastBirthday are entered
        if not ('LastBirthday' in data.keys() and 'FirstBirthday' in data.keys()):
            raise forms.ValidationError("You have to enter both First Birthday and Last Birthday. If they are the same, enter the same date twice.")

        # check that NumberOfJuveniles is indicated 
        if not 'NumberOfJuvenilesToAdd' in data.keys():
            raise forms.ValidationError("Please indicate how many newborns are to be entered into the database.")

        # check that FirstBirthday and LastBirthday are not more than BROOD_RANGE apart
        if (data['LastBirthday']-data['FirstBirthday']) > datetime.timedelta(Brood.BROOD_RANGE):
            raise forms.ValidationError("The dates you provided are further away from one another than we currently accept. Talk to HOB.")
        return data


class EditCommentCouplingForm(BirdlistForm):
    '''
    A form mainly to edit the comment field of a Coupling instance
    '''
    def __init__(self, *args, **kwargs):
        super(EditCommentCouplingForm, self).__init__(*args, **kwargs)
        self.fields['coupling_date'].widget = forms.HiddenInput()
        self.fields['cage'].widget = forms.HiddenInput()
        self.fields['couple'].widget = forms.HiddenInput()

    class Meta:
        model = Coupling
        exclude = ['separation_date', ]
