#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Bird', 'brood', models.ForeignKey, null=True, related_model='birdlist.Brood'),
    DeleteField('Bird', 'mother'),
    DeleteField('Bird', 'father')
]
#----------------------
