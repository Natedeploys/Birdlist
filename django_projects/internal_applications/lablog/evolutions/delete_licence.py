from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    DeleteField('Experiment', 'license')
]

