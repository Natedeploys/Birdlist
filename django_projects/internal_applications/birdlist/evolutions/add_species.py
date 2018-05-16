from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Bird', 'species', models.CharField, initial='ZF', max_length=255)
]




