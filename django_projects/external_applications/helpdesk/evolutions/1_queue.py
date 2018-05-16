#----- Evolution for helpdesk
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Queue', 'new_ticket_cc', initial=None, max_length=200),
    ChangeField('Queue', 'updated_ticket_cc', initial=None, max_length=200)
]
#----------------------

