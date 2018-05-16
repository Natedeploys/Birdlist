from django.dispatch import Signal

experiment_mod = Signal(providing_args=["author", "title"])

