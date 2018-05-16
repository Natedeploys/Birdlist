''' experiment specific helper functions '''

import os
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.conf import settings
from django.core.urlresolvers import reverse

from lablog.models import Experiment, Event
from lablog.utils.generic import order_and_sort

def delete_experiment_signal_receiver(sender, **kwargs):
    # currently not working, because of upstream bug:
    # http://code.djangoproject.com/ticket/6870

    instance = kwargs['instance']
    remove_animal_list_link_from_experiment(instance.id)
    
        
def remove_animal_list_link_from_experiment(experiment_id):
    # find a possibly associated activity and remove the link to this 
    # experiment
    experiment = Experiment.objects.get(id = experiment_id)
    try:
        activity = experiment.bird.get()
        activity.content_object = None
        activity.save()
        experiment.save()
    except:
        pass


def generate_bird_inline_form(username, nbr_extra = 1):
    # Generic formset to bind BirdList to Lablog
    from django.contrib.contenttypes.generic import generic_inlineformset_factory
    from birdlist.models import Activity
    from birdlist.forms.activity_forms import ActivityFormAddExperimentFromLablog
    
    GenericFormSet = generic_inlineformset_factory(Activity, form = ActivityFormAddExperimentFromLablog, extra = nbr_extra, can_delete = False)

    return GenericFormSet


def get_activity_type(query):
    from django.contrib.contenttypes.models import ContentType
    activity_type = ContentType.objects.get(app_label="birdlist", model="Activity")
    from django.core.exceptions import ObjectDoesNotExist
    try:
        activity_instance = activity_type.get_object_for_this_type(object_id = query.bird.pk_val)
        return activity_instance

    except ObjectDoesNotExist:
        return None


def get_activity_object(query):

    activity_instance = get_activity_type(query)
    if activity_instance:
        return activity_instance.content_object
    else:
        return None


# look up bird name for experiment - helper function
def get_birdname_for_experiment(query_object):

    activity_object = get_activity_type(query_object)
    if activity_object:
        bird_name = activity_object.bird
        bird_id = activity_object.bird.id
        from birdlist.models import Bird
        bird = Bird.objects.get(id = bird_id)
        phd_start_experiment = bird.get_phd(query_object.start_date)
        phd_end_experiment = bird.get_phd(query_object.end_date)
    else:
        bird_name = "none"
        phd_start_experiment = None
        phd_end_experiment = None
        bird = ''
        activity_object = ''
        
    return bird_name, bird, phd_start_experiment, phd_end_experiment, activity_object


## look up methods for all experiments - can be used in different views as well.
def query_latest(user, username, nbr_return=10):

    # Do not use get_list_or_404 here, because we don't want to raise an 
    # exception - instead we want to present a "create new experiment" option.
    exp_lablog = Experiment.objects.select_related().filter(author__username__exact=user)

    from lablog.views.basic.lablog_main import active_inactive_objects
    active_experiments, finished_experiments, experiments = active_inactive_objects(exp_lablog, nbr_return)
    
    from birdlist.models import Activity, Activity_Type
    # all "Experiment" activities that have NO object_id / content_object
    # assigned to them, are experiments created in the birdlist which are
    # not associated with a lablog experiment.
    experiment_to_add_from_birdlist = Activity.objects.filter(activity_type = \
        Activity_Type.objects.get(name='Experiment'), \
        originator__username__exact = user, object_id = None).order_by('-start_date')

    vdict = {
        'experiments': experiments,
        'active_experiments': active_experiments,
        'finished_experiments': finished_experiments,
        'experiments_in_animal_list': experiment_to_add_from_birdlist,
    }

    return vdict

def pluralize_str(number, string, pre_strg):

    if number == 1:
        sub_str = ' ' + string
    else:
        sub_str = ' ' + string + 's'

    return number.__str__() + ' ' + pre_strg + sub_str


def create_title(objects, string, pre_strg):

    number = objects.__len__()
    title = ''

    if number != 0:
        title = pluralize_str(number, string, pre_strg)

    return title

 
## remove thumbnail file names from list of files
def clean_file_list(media_files):

    clean_list = list()
    for i in media_files:
        if i.find(settings.THUMBNAIL_PREFIX) != 0:
            clean_list.append(i)

    return clean_list
 
## create the url for each file in media_files list
def get_media_file_urls(media_files, media_path):
    media_files = clean_file_list(media_files)

    file_urls = list()
    for x in media_files:
        file_urls.append(os.path.join(settings.LABLOG_MEDIA_URL, media_path, x))

    return file_urls, media_files

def get_media_dirs(query_object):
    import logging
    zipped = ''
    error_message = ''
    if query_object.media_path:
        try:
            # make sure user supplied path has "/" at the beginning and end of the name
            query_object.media_path = os.path.abspath(os.path.join(os.sep, query_object.media_path))
            media_path_relative = os.path.relpath(os.sep + query_object.media_path + os.sep)
            media_path = os.path.abspath(settings.LABLOG_MEDIA + media_path_relative)
            logging.debug("media_path: " + media_path)
            media_files = os.listdir(media_path)
            logging.debug("media files: ")
            logging.debug(media_files)
            media_file_urls, media_files = get_media_file_urls(media_files, media_path_relative)
            logging.debug(media_file_urls)
            logging.debug(media_files)
            zipped = zip(media_files, media_file_urls)
        except Exception, e:
            import sys
            tb = sys.exc_info()[2]
            logging.debug("line number: " + str(tb.tb_lineno))
            logging.debug(e)
            error_message = e
            zipped = ''

    return zipped, error_message


def generate_activity_formset_with_POST_data_from_experiment(request, username, GenericFormSet):

    new_data = copy_experiment_fields_to_activity(request, username)

    try:
        formset = GenericFormSet(new_data, prefix = 'bird')
    except IndexError, e:
        print e
        formset = ''

    return formset


def copy_experiment_fields_to_activity(request, username):
    # DO NOT REMOVE! very important to keep activity in sync with 
    # experiment!

    new_data = request.POST.copy()
    # copy all required (that is, required BEFORE validation) data and 
    # pass it on to the GenericFormSet - we know that our formset has 
    # only one entry, therefore we can directly index / address the 
    # correct form.
    from lablog.utils.generic import get_user_object
    user_object = get_user_object(username)
    
    new_data['bird-0-originator'] = user_object.id
    new_data['bird-0-start_date'] = new_data['start_date']
    new_data['bird-0-end_date'] = new_data['end_date']    
    new_data['bird-0-activity_content'] = new_data['title']

    return new_data


def fill_activity_formset_with_data_from_experiment(formset, experiment):
    # take the formset and extract the form            
    for form in formset.forms:
        # return "to-be-created" object
        tmpform = form.save(commit = False)
        # set the content_object to the just created experiment
        # this will automatically take care of the id & content_type 
        # fields
        tmpform.content_object = experiment
        # save it into the database
        tmpform.save()

# creates and returns the HTTP-REQUEST for 'list_event*' methods #
def return_event_list_object(request, username, queryset, entries_per_page, experiment, nbr_events, event_type_id=None, event_title=None):

    if not event_title:
        my_str = str(nbr_events)
        sub_str = 'Event'
        if nbr_events > 1 or nbr_events == 0:
            sub_str = 'Events'

        event_title =  my_str + " " + sub_str + " found"

    betweenform = load_betweenform(username, experiment.pk, event_type_id)
    from lablog.forms.lablogforms import TagEvent
    #  TagEvent(auto_id=False) won't work because the widget needs an ID!
    TagForm = TagEvent()

    return object_list(request, queryset = queryset,
            template_name = 'lablog/experiment/list_events.html', 
            paginate_by = int(entries_per_page), 
            template_object_name = 'event',
            extra_context = {'experiment': experiment, 
                            'event_title': event_title,
                            'selected_object': experiment, 
                            'betweenform': betweenform, 
                            'allow_user_sorting': 1, 
                            'TagForm': TagForm, } )


def load_betweenform(username, experiment_id, event_type_id=None):
    # quicklink for adding specific event type
    from lablog.forms.lablogforms import EventFormMinimal
    from lablog.models import Event, Event_Type

    betweenform = EventFormMinimal(username)

    # filter event_type selection by the event types that are actually used in this experiment
    event_list = Event.objects.filter(experiment = experiment_id)
    subselected = sorted(event_list.values_list('event_type'))
    uniques = []
    for i in subselected:
        bla = i[0]
        uniques.append(bla.__int__())

    all_events = Event_Type.objects.filter(id__in = uniques)
    betweenform.fields['event_type'].queryset = all_events

    # highlight currently selected filter
    if event_type_id:
        betweenform.fields["event_type"].initial = event_type_id

    return betweenform



def get_all_events(request, username, experiment_slug, event_type_id=None, year=None, month=None, day=None):
    
    """ different users might use the same slug, so we need to get all 
        experiments for the current user 
    """
    experiment = get_object_or_404(Experiment, author__username__exact=username, slug__exact=experiment_slug)

    "  show all events from all days by default.  "
    order, sort_dir = order_and_sort(request)
    event_list = Event.objects.filter(experiment = experiment.pk).select_related('event_type').order_by(order + 'date', order + 'time')


    " filter events by date if requested "
    if year:
        event_list = event_list.filter(date__year = year)

    if month:
        event_list = event_list.filter(date__month = month)

    if day:
        event_list = event_list.filter(date__day = day)

    " filter events by event_type if requested "
    if event_type_id:
        event_list = event_list.filter(event_type = event_type_id)


    return experiment, event_list

''' not needed anymore
def simple_search(query, terms=None):

    from django.db.models import Q

    if terms:
        results = query.filter(Q(text_field__icontains = terms))
    else:
        results = ''

    return results

'''

from django.contrib.auth.models import User
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import render_to_response
from django.template.context import RequestContext


from lablog.forms.lablogforms import ExperimentFormBasic
from lablog.models import Project, Protocol

class new_experiment_with_animal_wizard(FormWizard):

    def __call__(self, request, *args, **kwargs):
        """
         The __call__ method is called each time a new
         instance of the FormWizard is created.
         So, this is the place to set, among other things,
         initial values for the FIRST FORM in the wizard)
        """
        # self.step is always zero, but the first step will be called via GET
        if self.step == 0 and request.method == 'GET':
            extra_context =  kwargs['extra_context']
            username = extra_context.get('username')
            user = User.objects.get(username__exact = username)
            user_id = str(user.id)
            
            # it is impossible to set the queryset of a field here - we can only
            # define the default selection (self.initial)
            
            self.initial[(0)] = {
                'author': user_id,
                'project': Project.objects.filter(author__username__exact=username), 
                'protocol': Protocol.objects.filter(author__username__exact=username),
            }
            
        print "bla in _call_"
        print self
        return super(new_experiment_with_animal_wizard, self).__call__(request, *args, **kwargs)  


    def get_template(self, step):
        return 'lablog/basic/base_form_wizard.html'

    def parse_params(self, request, *args, **kwargs):
        extra_context =  kwargs['extra_context']
        self.username = extra_context.get('username')
        
    def render_template(self, request, form, previous_fields, step, context=None):
        
        context = context or {}
        # update the optional steps variable after each step so that the template
        # string get's displayed accordingly.
        if step == 2:
            self.extra_context['optional_steps'] = False
        else:
            self.extra_context['optional_steps'] = True
        
        self.extra_context['username'] = self.username
        context.update(self.extra_context)
        return render_to_response(self.get_template(step), dict(context,
            step_field=self.step_field_name,
            step0=step,
            step=step + 1,
            step_count=self.num_steps(),
            form=form,
            previous_fields=previous_fields
        ), context_instance=RequestContext(request))

    def process_step(self, request, form, step):
        
        # called after 1st step
        if step == 0:
            print "bla"
            # update activity with user given input.
            activity = self.activity
            activity.end_date = form.cleaned_data['end_date']
            activity.activity_content = form.cleaned_data['activity_content']
            self.activity = activity
            
            # set reasonable default values
            self.nbr_syls = None
            self.cause_of_exit = None
            self.end_date = form.cleaned_data['end_date']
            checkout_animal_from_database = form.cleaned_data['checkout_animal_from_database']
            self.checkout_animal_from_database = checkout_animal_from_database
            # remove CheckoutForm if user didn't select it.
            if not self.checkout_animal_from_database:
                if self.form_list_orig[-1] == CheckoutAnimalFromColonyFormShort:
                    form_list_copy = self.form_list
                    form_list_copy.remove(CheckoutAnimalFromColonyFormShort)
                    self.form_list = form_list_copy
        
        # called after 2nd step
        if step == 1:
            
            form_list_copy = self.form_list
            
            # skip 3rd step if no song has been recorded.
            exp_type = form.cleaned_data['exp_type']
            if exp_type == '1':
                form_list_copy.remove(ActivityFormExperimentCheckNbrSyls)
            
            self.form_list = form_list_copy
        
        # called after 3rd step, either nbr syls, or animal checkout
        if step == 2:
            if form.cleaned_data.has_key('nbr_syls'):
                nbr_syls = form.cleaned_data['nbr_syls']
                self.nbr_syls = nbr_syls
            if form.cleaned_data.has_key('cause_of_exit'):
                cause_of_exit = form.cleaned_data['cause_of_exit']
                self.cause_of_exit = cause_of_exit
            
        # called after 4th step, animal checkout
        if step == 3:
            cause_of_exit = form.cleaned_data['cause_of_exit']
            self.cause_of_exit = cause_of_exit
            
        
    def done(self, request, form_list):
        activity = self.activity
        activity.save()
        
        bird = activity.bird
        
        nbr_syls = self.nbr_syls
        if nbr_syls:
            if nbr_syls == '0':
                string = '"did not sing"'
            elif nbr_syls == '1':
                string = '"1 syl"'
            else:
                string = '"%s syls"' % nbr_syls
                
            # tag bird
            tag_object(bird, string)


        # checkout bird from database
        if self.checkout_animal_from_database:
            from birdlist.utils.bird import do_checkout_from_database
            if bird.reserved_by:
                do_cancel_reservation(bird)
            do_checkout_from_database(bird, self.end_date, self.cause_of_exit, request.user)

        return HttpResponseRedirect(reverse('bird_overview', args=(bird.id, )))



from birdlist.forms.birdlist_formsets import FindExperimentForm
from birdlist.models import Activity
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect

class merge_exp_form(FormWizard):
    def get_template(self, step):
        return 'lablog/basic/base_form_wizard.html'
        
    def parse_params(self, request, *args, **kwargs):
        extra_context =  kwargs['extra_context']
        self.username = extra_context.get('username')
        self.experiment_slug = extra_context.get('exp_slug')
       
    def process_step(self, request, form, step):
        
        if step == 0:
            bird = form.cleaned_data['bird']
            # doesn't work, because form instance is not accepted, only formName
            #self.form_list[1] = FindExperimentForm(bird)
            
        if step == 1:
            activity = form.cleaned_data['experiment']
            lablog_exp = Experiment.objects.get(slug = self.experiment_slug)
            animallist_activity = Activity.objects.get(id = activity.id)
            animallist_activity.content_object = lablog_exp
            animallist_activity.save()
            
        # __init__ will only be called for the non first form in 'form_list'
        # Change the __init__ # function of the FindExperimentForm to set
        # the correct choices - what a hack!
        def __init__(self, *args, **kw):
            super(FindExperimentForm, self).__init__(*args, **kw)
            self.fields['experiment'].queryset = Activity.objects.filter(activity_type__name='Experiment', bird__id = bird, object_id = None)
        FindExperimentForm.__init__ = __init__
        
    def done(self, request, form_list):
        return HttpResponseRedirect(reverse('detail_experiment', args=(self.username, self.experiment_slug,)))

    
