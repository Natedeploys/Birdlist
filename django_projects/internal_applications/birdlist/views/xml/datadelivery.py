
from django.core import serializers
from django.http import HttpResponse

from birdlist.models import Bird, Activity


def bird_info(request, birdname):
    '''
    '''
    bird = Bird.objects.filter(name=birdname)
    bird_xml = serializers.serialize('xml', bird)
    return HttpResponse(bird_xml, content_type='text/xml') 


def experiments_for_bird(request, birdname):
    '''
    '''
    try: 
        bird = Bird.objects.get(name=birdname)
    except:
        return HttpResponse('could not fetch bird requested') 
    exp = Activity.objects.filter(bird=bird, activity_type__name='Experiment')
    exp_xml = serializers.serialize('xml', exp)

    return HttpResponse(exp_xml, content_type='text/xml') 
