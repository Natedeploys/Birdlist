#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Note', 'schedule', models.PositiveIntegerField, initial=1)
]
#----------------------
