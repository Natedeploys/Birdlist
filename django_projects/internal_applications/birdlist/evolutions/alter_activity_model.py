from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Activity', 'originator', models.ForeignKey, initial=2, related_model='auth.User'),
    DeleteField('Activity', 'comment'),
]

