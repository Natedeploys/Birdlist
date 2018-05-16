#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Bird', 'coupling_status', models.PositiveIntegerField, initial=0),
    DeleteField('Bird', 'do_not_couple')
]

