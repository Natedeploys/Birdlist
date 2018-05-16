#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Coupling', 'separation_date', initial=None, null=True)
]
#----------------------
