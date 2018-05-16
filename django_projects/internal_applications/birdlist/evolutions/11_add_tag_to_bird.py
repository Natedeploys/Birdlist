#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models
from tagging_autocomplete.models import TagAutocompleteField

MUTATIONS = [
    AddField('Bird', 'tags', TagAutocompleteField, initial='', max_length=255)
]
#----------------------
