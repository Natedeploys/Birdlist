#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models
import datetime

MUTATIONS = [
    AddField('Activity', 'timestamp_created', models.DateTimeField, initial=datetime.datetime(1991, 8, 25, 22, 57)),
    AddField('Activity', 'timestamp_modified', models.DateTimeField, initial=datetime.datetime(1991, 8, 25, 22, 57))
]
#----------------------

