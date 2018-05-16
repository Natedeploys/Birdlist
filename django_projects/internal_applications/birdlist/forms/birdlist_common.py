from django.forms import ModelForm
import django.forms as forms

class BirdlistForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BirdlistForm, self).__init__(*args, **kwargs)
