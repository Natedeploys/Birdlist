#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Experiment', 'license', models.PositiveSmallIntegerField, initial=74)
]
#----------------------
