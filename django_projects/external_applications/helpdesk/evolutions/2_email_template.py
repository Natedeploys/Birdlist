#----- Evolution for helpdesk
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('EmailTemplate', 'locale', models.CharField, max_length=10, null=True),
    ChangeField('EmailTemplate', 'template_name', initial=None, unique=False)
]
#----------------------
