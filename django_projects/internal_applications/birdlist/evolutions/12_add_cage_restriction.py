#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Cage', 'restriction', models.PositiveIntegerField, null=True)
]
#----------------------
