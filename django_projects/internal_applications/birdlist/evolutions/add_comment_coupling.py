#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Coupling', 'comment', models.TextField, null=True)
]
#----------------------
