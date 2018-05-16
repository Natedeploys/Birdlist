#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Coupling', 'type', models.PositiveIntegerField, initial=0)
]
#----------------------
