from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Activity', 'activity_type', models.ForeignKey, initial=1, related_model='birdlist.Activity_Type')
]
