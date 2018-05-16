#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Event', 'schedule', models.PositiveIntegerField, initial=1)
]
#----------------------
