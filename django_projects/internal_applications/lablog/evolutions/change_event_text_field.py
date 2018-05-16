#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Event', 'text_field', initial=None, max_length=2048)
]
#----------------------
