#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Cage', 'function', models.PositiveIntegerField, initial=0),
    DeleteField('Cage', 'is_breeding_cage')
]
#----------------------
