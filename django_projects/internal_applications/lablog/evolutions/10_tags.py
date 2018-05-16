#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models
from tagging_autocomplete.models import TagAutocompleteField

MUTATIONS = [
    AddField('Event', 'tags', TagAutocompleteField, initial='', max_length=255)
]
#----------------------
