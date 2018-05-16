#----- Evolution for lablog
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Event_Type', 'flag_color', models.CharField, max_length=255, null=True),
    ChangeField('Event', 'text_field', initial=None, null=True)
]
#----------------------
