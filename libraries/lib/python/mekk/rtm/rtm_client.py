# -*- coding: utf-8 -*-

from collections import namedtuple
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import tzutc
from mekk.rtm.rtm_connector import RtmException
import datetime

############################################################
# Helper structures (representations of RTM data)
############################################################

"""
See RtmClient class below for API documentation.

The following structures (namedtuples) are used to represent
data downloaded from RememberTheMilk

List (normal list):
- id (string) - unique id
- name (string) - list name
- archived (bool) - is the list archived (true) or active (false)
"""
List = namedtuple('List', 'id name archived')  

"""
Smart list (query):
- id, name, archived - as in List
- filter (string) - smartlist query (as defined via web interface)
"""
SmartList = namedtuple('SmartList', 'id name filter archived')

"""
Note (extra text appended to task)
- id (string) - unique id (inside task)
- title (string) - note title
- body (string) - note text (can contain newlines)
"""
Note = namedtuple('Note', 'id title body')

"""
Unique identification of individual task:
- list_id (string) - identification of list the task belons to
- taskseries_id (string) - ...
- task_id (string) - id of task as such
"""
TaskKey = namedtuple('TaskKey', 'list_id task_id taskseries_id')

"""
All task data:
- key (TaskKey) - task identification
- name (string) - task description
- tags (list of strings, can be empty) - all task tags
- notes (list of Note objects, can be empty) - all notes appended to task
- due (datetime.datetime or None) - due date, can be None when not set
- estimate (string or None) - estimated cost in RTM jargon (f.e. "5 hours"), None when unset
- priority (int or None) - priority (1,2,3 or None when unset)
- completed (bool) - is the task already completed?
- postponed (int) - how many times task was postponed (0 if never)
- repeat (string or None) - textual description of repeating clause
     (currently sth like "every FREQ=DAILY;INTERVAL=3", in the future
      can change to sth more sensible)
- url (string or None) - url bound to task if any
- deleted (bool) - set to true if the task has been deleted (can happen only
      in result of delete method)
"""
Task = namedtuple('Task', 'key name tags notes due estimate priority completed postponed repeat url deleted')

class RtmDataException(RtmException): 
    """
    Exception thrown when the data structure is not understood by the library.
    """
    pass


# Implementation note: I abstract TaskSeries->Task hierarchy, using
# only Tasks (and adding taskseries as attribute to them). While taskseries
# help aggregate some attributes in case of repeating tasks, I don't feel
# they are of much use from the client point of view.

class RtmClient(object):
    """
    Wrapper for RTM client calls. Handles listing, creating
    and modifying lists, tags, locations, and tasks.

    Apart from wrapping RememberTheMilk API quirks it:

    - keeps the cache of known lists to avoid re-downloading them and
      handles duplicate detection in case of lists (so the same list
      is not created again)

    - abstracts over some differences in data structure and format
      providing uniform API.
      
    All updates are performed inside single timeline (Rtm undo
    context) unless set_undo_point routine is called.
    """
    
    def __init__(self, connector):
        """
        Initializes object. 

        @param connector authorized mekk.rtm.RtmConnector object used to
               handle communication. Usually created using
               functions from mekk.rtm.connect module
        """
        self.connector = connector
        self._list_cache = None      # name -> List
        self._smartlist_cache = None # name -> SmartList
        self._timeline = None

    def find_or_create_list(self, list_name):
        """
        Looks for the (normal) list of given name.
        If such list does not exist, creates it.

        Uses list cache for better performance.

        Returns List object representing given list
        """
        self._load_list_cache_if_necessary()
        list_info = self._list_cache.get(list_name)
        if list_info:
            #if list_info.archived:
            #    self.unarchive_list(list_info.id)
            return list_info
        timeline = self._get_timeline()

        r = self.connector.call(
            "rtm.lists.add",
            timeline = timeline,
            name = list_name)
        new_list = self._process_list_reply(r['list'])
        return new_list

    def unarchive_list(self, list_id):
        """
        Unarchives list of given id, returns the List or SmartList
        object representing list state after the operation.
        """
        r = self.connector.call(
            "rtm.lists.unarchive", 
            timeline = self._get_timeline(),
            list_id = list_id)
        return self._process_list_reply(r['list'])

    def archive_list(self, list_id):
        """
        Archives list of given id, returns the List or SmartList
        object representing list state after the operation.
        """
        r = self.connector.call(
            "rtm.lists.archive",
            timeline = self._get_timeline(),
            list_id = list_id)
        return self._process_list_reply(r['list'])

    def delete_list(self, list_id):
        """
        Deletes list of given id. Returns List object showing before-deletion data
        """
        r = self.connector.call(
            "rtm.lists.delete",
            timeline = self._get_timeline(),
            list_id = list_id)
        return self._process_list_reply(r['list'])

    def known_lists(self):
        """
        Returns all known lists (except smartlists, only true lists are returned).

        Return value is a list of List namedtuples
        """
        self._load_list_cache_if_necessary()
        return self._list_cache.values()

    def known_smart_lists(self):
        """
        Returns all known smart lists.

        Return value is a list of SmartList namedtuples
        """
        self._load_list_cache_if_necessary()
        return self._smartlist_cache.values()

    def create_task(self, task_name,
                    list_id = None,
                    tags = [], 
                    completed = False,
                    priority = None,
                    due_date = None,
                    estimate = None,
                    repeat = None,
                    url = None,
                    notes = [],
                    ):
        """
        Creates new task and sets some attributes. Returns TaskKey
        object needed to update the task later.

        @param task_name 
        @param list_id list identifier, can be None (then Inbox is used)
        @param tags list of tags (note: tags can't contain ',')
        @param completed should task be immediately marked as completed?
        @param priority  1, 2, or 3 (or None)
        @param due_date due date (datetime.date or ISO 8601 text, if given date is zone-unaware, it is assumed to be UTC)
        @param estimate estimated cost (text like "3 days 2 hours 40 minutes")
        @param repeat task repeating clause (text like "Every Tuesday", "Every month on the 4th", "Every week until 1/1/2007", "After a week" etc. See http://www.rememberthemilk.com/help/answers/basics/repeatformat.rtm )
        @param url webpage related to the task (or None)
        @param notes list of pairs (title, text) representing notes to be added to the task

        @returns Task object representing the task
        """
        timeline = self._get_timeline()
        r = self.connector.call("rtm.tasks.add",
                                timeline = timeline,
                                list_id = list_id,
                                name = task_name)
        if not list_id:
            # addTags and other methods require it
            list_id = r['list']['id']
        task = RtmClient._parse_task(list_id, RtmClient._ensure_element_is_singular(r['list']['taskseries']))

        self.update_task(task.key,
                         add_tags = tags,
                         completed = completed,
                         priority = priority,
                         due_date = due_date,
                         estimate = estimate,
                         repeat = repeat,
                         url = url,
                         notes = notes,
                         )

        return task

    def update_task(self, task_key,
                    add_tags = [],  # add tags without changing existing
                    set_tags = None, # If specified, list of tags, drop old tags
                    completed = False,
                    priority = None,
                    due_date = None,
                    estimate = None,
                    repeat = None,
                    url = None,
                    notes = [],
                    ):
        """
        Updates given task attributes. All parameters has
        the same semantic as in create_task except  set_tags,
        which, if specified, resets tag list to given items
        (removing all old tags). 
        """
        timeline = self._get_timeline()

        r = None

        if set_tags is not None:
            tag_text = ",".join(set_tags)
            r = self.connector.call(
                "rtm.tasks.setTags",
                timeline = timeline,
                tags = tag_text,
                **task_key._asdict())            
            
        if add_tags:
            tag_text = ", ".join(add_tags)
            r = self.connector.call(
                "rtm.tasks.addTags",
                timeline = timeline,
                tags = tag_text,
                **task_key._asdict())

        if completed:
            r = self.connector.call(
                "rtm.tasks.complete",
                timeline = timeline,
                **task_key._asdict())

        if priority:
            r = self.connector.call(
                "rtm.tasks.setPriority",
                timeline = timeline,
                priority = str(priority),
                **task_key._asdict())

        if due_date:
            r = self.connector.call(
                "rtm.tasks.setDueDate",
                timeline = timeline,
                due = RtmClient._prepare_date_for_sending(due_date),
                parse = "1", # has_due_time = 1
                **task_key._asdict())

        if estimate:
            r = self.connector.call(
                "rtm.tasks.setEstimate",
                timeline = timeline,
                estimate = estimate,
                **task_key._asdict())

        if repeat:
            r = self.connector.call(
                "rtm.tasks.setRecurrence",
                timeline = timeline,
                repeat = repeat,
                **task_key._asdict())
            
        if url:
            r = self.connector.call(
                "rtm.tasks.setURL",
                timeline = timeline,
                url = url,
                **task_key._asdict())

        if r:
            task = RtmClient._parse_task(task_key.list_id,
                                         RtmClient._ensure_element_is_singular(r['list']['taskseries']))
        else:
            task = None

        for (note_title, note_text) in notes:
            rn = self.add_task_note(task_key,
                               note_title = note_title, note_text = note_text)
            if task:
                task.notes.append(rn)

        return task

    def move_task(self, task_key, new_list_id):
        """
        Moves given task to new list. Returns current task state.
        Note that task key changes after this operation!
        """
        timeline = self._get_timeline()
        r = self.connector.call(
            "rtm.tasks.moveTo",
            timeline = timeline,
            from_list_id = task_key.list_id,
            to_list_id = new_list_id,
            taskseries_id = task_key.taskseries_id,
            task_id = task_key.task_id)
        task = RtmClient._parse_task(
            new_list_id,
            RtmClient._ensure_element_is_singular(r['list']['taskseries']))
        return task

    def add_task_note(self, task_key, 
                      note_title, note_text):
        """
        Adds new note to the task. 

        @param task_key: task identity
        @param note_title: note label (invisible?)
        @param note_text: actual body
        @returns: Note object repesenting note
        """
        timeline = self._get_timeline()
        r = self.connector.call(
            "rtm.tasks.notes.add",
            timeline = timeline,
            note_title = note_title, note_text = note_text,
            **task_key._asdict())
        return RtmClient._parse_note(r['note'])

    def delete_task(self, task_key):
        """
        Deletes given task.
        @returns: Task data after operation (with deleted=True)
        """
        timeline = self._get_timeline()
        r = self.connector.call(
            "rtm.tasks.delete",
            timeline = timeline,
            **task_key._asdict())
        return RtmClient._parse_task(task_key.list_id,
                                     RtmClient._ensure_element_is_singular(r['list']['taskseries']))

    def find_tasks(self,
                   list_id = None, 
                   filter = None,
                   last_sync = None):
        """
        Finds all asks matchin given criteria: belonging to specified
        list (or any list if missing), satisfying filter if present,
        and modified since last_sync (if present). last_sync can be
        specified as datetime

        Filter syntax: http://www.rememberthemilk.com/help/answers/search/advanced.rtm

        The routine works as generator and yields all found tasks. To
        get the results as list, just wrap it with list(), for example::
        
            my_items = list(client.find_tasks(list_id = inbox.id))
        """
        r = self.connector.call(
            "rtm.tasks.getList",
            list_id = list_id,
            filter = filter,
            last_sync = last_sync)
        tasks = r['tasks'].get('list', [])
        if type(tasks) is dict:
            tasks = [ tasks ]
        for task_list in tasks:
            list_id = task_list['id']
            for taskseries in RtmClient._wrap_element_as_list_if_singular(task_list['taskseries']):
                task_block = taskseries['task']
                if type(task_block) is not list:
                    task_block = [ task_block ]
                for task in task_block:
                    yield RtmClient._parse_task(list_id, taskseries, task)

    def set_undo_point(self):
        """
        Force creation of new timeline. Timelines are not really used 
        in the library yet, so it is more marker of possible future 
        development than anything else.
        """
        # Just forgetting previous timeline. New one will be created before first update
        self._timeline = None

    def _get_timeline(self):
        if self._timeline is None:
            r = self.connector.call(
                "rtm.timelines.create")
            self._timeline = r['timeline']
        return self._timeline

    def _load_list_cache_if_necessary(self):
        if self._list_cache is None:
            r = self.connector.call(
                "rtm.lists.getList")
            self._list_cache = {}
            self._smartlist_cache = {}
            for l in r['lists']['list']:
                self._process_list_reply(l)

    def _process_list_reply(self, list_dic):
        """
        Converts XML list data (as returned by many rtm.lists commands)
        to List or SmartList tuple and updates internal cache for this list.
        """
        id = list_dic['id']
        name = list_dic['name']
        archived = RtmClient._parse_flag(list_dic['archived'])
        deleted = RtmClient._parse_flag(list_dic['deleted'])
        if not RtmClient._parse_flag(list_dic['smart']):
            r = List(
                id = id,
                name = name,
                archived = archived)
            if not deleted:
                self._list_cache[name] = r
            else:
                del self._list_cache[name]
        else:
            r = SmartList(
                id = id,
                name = name,
                archived = archived,
                filter = list_dic['filter'])
            if not deleted:
                self._smartlist_cache[name] = r
            else:
                del self._smartlist_cache[name]
        return r

    @staticmethod
    def _parse_task(list_id, taskseries_blk, task_blk = None):
        """
        Converts XML data to Task. If task_blk is not given, assumes first
        """
        if task_blk is None:
            task_blk = taskseries_blk['task']

        tags = RtmClient._unwrap_optional_element(taskseries_blk['tags'], 'tag', [])
        notes = RtmClient._unwrap_optional_element(taskseries_blk['notes'], 'note', [])

        return Task(
            key = TaskKey(list_id = list_id, taskseries_id = taskseries_blk['id'], task_id = task_blk['id']),
            name = taskseries_blk['name'],
            tags = tags,
            notes = [ RtmClient._parse_note(n) for n in notes ],
            due = RtmClient._parse_due(task_blk['due']),
            estimate = RtmClient._parse_estimate(task_blk['estimate']),
            priority = RtmClient._parse_priority(task_blk['priority']),
            completed = RtmClient._parse_completed(task_blk['completed']),
            postponed = RtmClient._parse_postponed(task_blk['postponed']),
            repeat = RtmClient._parse_rrule(taskseries_blk.get('rrule')),
            url = RtmClient._parse_url(taskseries_blk.get('url', '')),
            deleted = RtmClient._parse_deleted(task_blk['deleted']),
            )

    @staticmethod
    def _parse_date(date_attr):
        if date_attr:
            return dateutil_parse(date_attr)
        else:
            return None

    _parse_due = _parse_date
    _parse_completed = _parse_date
    _parse_deleted = _parse_date

    @staticmethod
    def _parse_flag(flag_text):
        """
        Parses logical flag set as "1" or "0" (and sometimes ""). Returns True/False
        """
        return bool(int(flag_text or "0"))
        
    @staticmethod
    def _parse_postponed(txt):
        return int(txt)

    @staticmethod
    def _parse_txt_treating_empty_as_none(txt):
        if txt:
            return txt
        else:
            return None

    _parse_estimate = _parse_txt_treating_empty_as_none
    _parse_url = _parse_txt_treating_empty_as_none

    @staticmethod
    def _parse_priority(txt):
        if txt and txt != "N":
            return int(txt)
        else:
            return None

    @staticmethod
    def _parse_rrule(rrule_blk):
        # TODO: convert those ugly FREQ=DAILY;INTERVAL=1 back to 1 day etc
        if not rrule_blk:
            return None
        if rrule_blk.get('after'):
            pfx = "after"
        elif rrule_blk.get('every'):
            pfx = "every"
        return pfx + " " + rrule_blk['$t']

    @staticmethod
    def _parse_note(note_blk):
        return Note(id = note_blk['id'],
                    title = note_blk['title'],
                    body = note_blk['$t'])
            
    @staticmethod
    def _prepare_date_for_sending(some_date):
        """
        Normalizes date before posting to RTM server: flags it as UTC if it is zoneless,
        converts to string if it is datetime.date or datetime.datetime.
        """
        if type(some_date) is datetime.date:
            return some_date.isoformat() + "T00:00:00Z"
        if not ((type(some_date) is datetime.datetime)):
            some_date = dateutil_parse(some_date)
        if not some_date.tzinfo:
            some_date = some_date.replace(tzinfo=tzutc())
        return some_date.isoformat()

    @staticmethod
    def _unwrap_optional_element(item, tag_name, default_value=[]):
        """
        Handles the case when given element either contains empty list, or subdictionary with
        interesting data pointed by single key. Namely the case of tags/notes which can
        look so:

           "tags": []

        or so:

           "tags":{"tag":["@dom","testy"]}

        or even so:

           "tags":{"tag":"@dom"}
        
        @param item analyzed element in the tree (for the above example, either [] or {"tag":["@dom","testy"]})
        @param tag_name name of the sub-item
        @return value of the subitem, or default value (used when empty list is provided)
        """
        if type(item) is list:
            if item != []:
                raise RtmDataException("Block expected to be empty list or dictionary is nonempty list: %s\nNotify developer" % str(item))
            return default_value
        else:
            v = item[tag_name]
            if type(v) is not list:
                return [v]
            return v

    @staticmethod
    def _wrap_element_as_list_if_singular(item):
        """
        Handles the case, when some element either is a list of items (usually list of dictionaries),
        or single item. Example case is that of taskseries, which happen to be:

           "taskseries":[
              {"id":999, ... },
              {"id":888, ... },
           ]

        but also:

           "taskseries":{"id":999, ... }

        Always returns the list (for the latter case, consisting of single element).
        """
        if type(item) is list:
            return item
        else:
            return [item]

    @staticmethod
    def _ensure_element_is_singular(item):
        """
        Handles the same duality as _wrap_element_as_list_if_singular but expects
        exactly one item (be it on the list, or without it), otherwise raises exception
        """
        l = RtmClient._wrap_element_as_list_if_singular(item)
        if len(l) != 1:
            raise RtmDataException("Expected exactly one item, got less or more: %s\nNotify developer." % str(item))
        return l[0]
