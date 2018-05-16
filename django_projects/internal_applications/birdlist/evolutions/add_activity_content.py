from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Activity', 'activity_content', models.TextField, null=True)
]

