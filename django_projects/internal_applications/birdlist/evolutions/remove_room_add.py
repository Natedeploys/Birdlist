#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Cage', 'room', models.ForeignKey, initial=1, related_model='birdlist.LabRoom')
]
#----------------------
