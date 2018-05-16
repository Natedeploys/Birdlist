''' EVENT helper functions '''

from tagging.utils import edit_string_for_tags
from lablog.utils.generic import sync_tags_with_object

## look up methods for all event_types - can be used in different views as well.
def sync_tags_with_event(Tag, query_object):
    sync_tags_with_object(Tag, query_object)

