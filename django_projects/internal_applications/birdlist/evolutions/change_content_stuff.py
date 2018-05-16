from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Activity', 'content_type', initial=None, null=True),
    ChangeField('Activity', 'object_id', initial=None, null=True)
]

