#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Bird', 'do_not_couple', models.BooleanField, initial=False),
    AddField('Bird', 'missing', models.BooleanField, initial=False),
    AddField('Bird', 'outbreeder', models.BooleanField, initial=False)
]
#----------------------
