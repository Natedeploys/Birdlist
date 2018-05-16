from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Birdlist_Activity', 'animal_experiment_licence', models.ForeignKey, null=True, related_model='birdlist.Animal_Experiment_Licence')
]

