#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('LabRoom', 'in_use', models.BooleanField, initial=True),
    AddField('Bird', 'missing_since', models.DateField, null=True),
    AddField('Bird', 'reserved_by', models.ForeignKey, null=True, related_model='auth.User'),
#    AddField('Bird', 'brood', models.ForeignKey, null=True, related_model='birdlist.Brood'),
    AddField('Bird', 'date_of_birth', models.DateField, null=True),
    DeleteField('Bird', 'reserved'),
    DeleteField('Bird', 'missing'),
    DeleteField('Bird', 'outbreeder'),
#    DeleteField('Bird', 'father'),
    DeleteField('Bird', 'birthday'),
#    DeleteField('Bird', 'mother'),
    AddField('Activity', 'end_date', models.DateField, null=True),
    AddField('Activity', 'start_date', models.DateField, initial='2007-01-01'),
    DeleteField('Activity', 'date')
]
#----------------------
