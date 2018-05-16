#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Bird', 'comment', models.TextField, null=True),
    AddField('Bird', 'reserved', models.BooleanField, initial=False),
    AddField('Bird', 'father', models.ForeignKey, null=True, related_model='birdlist.Bird'),
    AddField('Bird', 'mother', models.ForeignKey, null=True, related_model='birdlist.Bird'),
    AddField('Bird', 'reserved_until', models.DateField, null=True)
]
#----------------------
