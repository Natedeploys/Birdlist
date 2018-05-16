#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Experiment', 'data', models.PositiveIntegerField, null=True)
]
#----------------------
