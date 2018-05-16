import django.forms as forms
from django.contrib.admin.widgets import AdminDateWidget
from birdlist.models import Activity, Bird, Cage, Activity_Type, Coupling
from lablog.forms.lablogforms import LablogForm

from songbird.widgets.widgets import SelectWithPop #, MultipleSelectWithPop

from ajax_filtered_fields.forms import ForeignKeyByLetter
from django.conf import settings

from autocomplete.widgets import AutoCompleteWidget


class FindBirdForm(forms.Form):
    bird = forms.CharField(widget=AutoCompleteWidget('birdname'))


class MyActivityChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s - %s); by '%s'" % (obj.activity_content, obj.start_date, obj.end_date, obj.originator)


class FindExperimentForm(forms.Form):
    experiment = MyActivityChoiceField(queryset = Activity.objects.all())


class FindBirdsForNewCouple(forms.Form):
    male = forms.CharField(widget=AutoCompleteWidget('male_bird'))
    female = forms.CharField(widget=AutoCompleteWidget('female_bird'))
    type = forms.TypedChoiceField(choices = Coupling.COUPLING_TYPE_CHOICES)
    
    
from django.core.exceptions import ValidationError
class AskBreedingSuccess(forms.Form):
    choices = (
            ('none', '---'),
            (Bird.COUPLING_DO_NOT_COUPLE, 'do not couple'),
            (Bird.COUPLING_BREEDER, 'good breeder'),
            (Bird.COUPLING_TRY_BREEDING_AGAIN, 'semi-ok breeder'),
    )
    breeder_status = forms.TypedChoiceField(choices = choices)
    evaluate_breeding = forms.BooleanField(initial = True)
    def __init__(self, *args, **kwargs):
        super(AskBreedingSuccess, self).__init__(*args, **kwargs)
        self.fields['breeder_status'].help_text = "Was this a successful couple?"
        self.fields['breeder_status'].label = "Coupling status"
        self.fields['evaluate_breeding'].widget = forms.HiddenInput()

    def clean_breeder_status(self, *args, **kwargs):
        if self.cleaned_data['breeder_status']:
            if self.cleaned_data['breeder_status'] == 'none':
                raise ValidationError('Please tell us more about the breeding success of this couple. Thanks!')
        return self.cleaned_data['breeder_status']
    

class FindCageForSeparatedCouple(forms.Form):
    cage_male = forms.CharField(widget=AutoCompleteWidget('cage_for_separation'))
    cage_female = forms.CharField(widget=AutoCompleteWidget('cage_for_separation'))

# seems not to work -> has no attribute 'fields'
#   def __init__(self, *args, **kwargs):
#       super(FindCageForSeparatedCouple, *args, **kwargs)
#       self.fields['cage_male'].help_text = 'Choose the new cage for the male here.'
#       self.fields['cage_female'].help_text = 'Choose the new cage for the female here.'


class FindCageForSeparatedCoupleAskBreedingSuccess(FindCageForSeparatedCouple, AskBreedingSuccess):
    def __init__(self, *args, **kwargs):
        super(FindCageForSeparatedCoupleAskBreedingSuccess, self).__init__(*args, **kwargs)


class FindCageForFamilyMove(forms.Form):
    cage = forms.CharField(widget=AutoCompleteWidget('cage_for_separation'))
    confirm = forms.BooleanField()
    def __init__(self, *args, **kwargs):
        super(FindCageForFamilyMove, self).__init__(*args, **kwargs)
        self.fields['cage'].help_text = "Please tell us where you want to move this family."
        self.fields['confirm'].help_text = "Please confirm that you want to move this family."


class FindCageForBroodAndMotherMove(FindCageForFamilyMove):
    def __init__(self, *args, **kwargs):
        super(FindCageForBroodAndMotherMove, self).__init__(*args, **kwargs)
        self.fields['cage'].help_text = "Please tell the cage name into which the youngest brood and the mother should be moved."
        self.fields['confirm'].help_text = "Please confirm that you want to move the youngest brood and the mother."


class FindCageForBroodAndMotherMoveAskBreedingSuccess(FindCageForBroodAndMotherMove, AskBreedingSuccess):
    def __init__(self, *args, **kwargs):
        super(FindCageForBroodAndMotherMoveAskBreedingSuccess, self).__init__(*args, **kwargs)


class ReserveBirdForm(forms.Form):
    reserve_until = forms.DateField(widget=AdminDateWidget())
    def __init__(self, *args, **kwargs):
        super(ReserveBirdForm, self).__init__(*args, **kwargs)
        self.fields['reserve_until'].help_text = "Please provide day until which we should reserve this animal for you."


class CheckoutAnimalFromColonyFormShort(forms.Form):
    cause_of_exit = forms.ChoiceField(choices = Bird.CAUSE_OF_EXIT_CHOICES)
    confirm = forms.BooleanField()
    def __init__(self, *args, **kwargs):
        super(CheckoutAnimalFromColonyFormShort, self).__init__(*args, **kwargs)
        self.fields['cause_of_exit'].help_text = "Please provide the reason why this bird is leaving. We will use today's date as timestamp of removal."
        self.fields['cause_of_exit'].label = "Reason for removal"
        self.fields['cause_of_exit'].initial = Bird.EXIT_NONE
        self.fields['confirm'].help_text = "Please confirm that you want to check this bird ouf of our system."

    # force user to select a cause of exit.
    def clean_cause_of_exit(self, *args, **kwargs):
        if self.cleaned_data['cause_of_exit']:
            if self.cleaned_data['cause_of_exit'] == str(Bird.EXIT_NONE):
                raise ValidationError('Please select a cause of exit.')
        return self.cleaned_data['cause_of_exit']

class CheckoutAnimalFromColonyForm(CheckoutAnimalFromColonyFormShort):
    exit_date = forms.DateField()
    def __init__(self, *args, **kwargs):
        super(CheckoutAnimalFromColonyForm, self).__init__(*args, **kwargs)
        self.fields['exit_date'].widget = AdminDateWidget()


class SelectCageForm(forms.Form):
    cage = ForeignKeyByLetter(Cage, field_name="name")

    def __init__(self, *args, **kwargs):
        super(SelectCageForm, self).__init__(*args, **kwargs)
        self.fields['cage'].queryset = Cage.objects.exclude(function=Cage.FUNCTION_NOTUSEDANYMORE)


class SexAnimalForm(forms.Form):
    sex = forms.TypedChoiceField(choices = (('none', '---'), (Bird.SEX_MALE, 'male'), (Bird.SEX_FEMALE, 'female')))


class BirdForm(LablogForm):

    father = ForeignKeyByLetter(Bird, field_name="name")
    mother = ForeignKeyByLetter(Bird, field_name="name")

    def __init__(self, *args, **kwargs):
        super(BirdForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget      = AdminDateWidget()
        self.fields['cage'].widget          = SelectWithPop(self.user, '/birdlist/cage')
        self.fields['cage'].queryset        = Cage.objects.all()
        self.fields['reserved_until'].widget = AdminDateWidget()
        self.fields['exit_date'].widget     = AdminDateWidget()
        #self.fields['father'].widget        = SelectWithPop(self.user, '/birdlist/bird')
        self.fields['father'].queryset      = Bird.objects.filter(sex = Bird.SEX_MALE)
        #self.fields['mother'].widget        = SelectWithPop(self.user, '/birdlist/bird')
        self.fields['mother'].queryset      = Bird.objects.filter(sex = Bird.SEX_FEMALE)

    class Meta:
        model = Bird


class CageForm(LablogForm):
    def __init__(self, *args, **kwargs):
        super(CageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Cage

