from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    DeleteModel('Birdlist_Activity_Type'),
    DeleteModel('Birdlist_Activity')
]

