from birdlist.views.bird import bird_main
from birdlist.models import Bird

from time import time

birdy = Bird.objects.get(name__exact='y16p-s2')

start_time = time()

bird_main.find_offspring(birdy.id)

end_time = time()

print 'find_offspring: %s' % (end_time-start_time)


start_time = time()

bird_main.find_offspring_new(birdy.id)

end_time = time()

print 'find_offspring_new: %s' % (end_time-start_time)


start_time = time()

bird_main.find_offspring_new2(birdy.id)

end_time = time()

print 'find_offspring_new2: %s' % (end_time-start_time)
