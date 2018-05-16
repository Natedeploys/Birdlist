''' EVENT_TYPE helper functions '''

from lablog.models import Event_Type

## look up methods for all event_types - can be used in different views as well.
def query_latest(user, username, order):

    event_types = Event_Type.objects.filter(author__username__exact=user).order_by(order + 'display_order')

    vdict = {
        'event_types': event_types,
        'nbr_events': event_types.__len__(),
    }

    return vdict

