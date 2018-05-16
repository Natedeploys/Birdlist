#----- Evolution for birdlist
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Bird', 'name_unique', initial=None, null=True)
]
#----------------------
