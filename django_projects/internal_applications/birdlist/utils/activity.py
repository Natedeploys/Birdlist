from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from birdlist.forms.activity_forms import ActivityFormExperimentCheckIfSongRecorded, ActivityFormExperimentCheckNbrSyls, ActivityFormExperimentClose, ActivityFormExperimentCloseHideCheckoutOption
from birdlist.forms.birdlist_formsets import CheckoutAnimalFromColonyFormShort
from birdlist.utils.bird import do_cancel_reservation
from lablog.utils.generic import tag_object
from birdlist.models import Activity


def allow_checkout_from_db(request, bird):
    ''' checks whether we can checkout an animal while closing an experiment '''
    
    # if not (not reserved, or reserved by myself, and I have the only open experiment)
    if not ((Activity.objects.filter(bird__id = bird.id, activity_type__name = 'Experiment', end_date = None, originator = request.user).__len__() == 1) \
                and (bird.reserved_by == None or bird.reserved_by == request.user)):
        return False
    else:
        return True


class close_experiment_wizard(FormWizard):

    def __call__(self, request, *args, **kwargs):
        """
         The __call__ method is called each time a new
         instance of the FormWizard is created.
         So, this is the place to set, among other things,
         initial values for the first form in the wizard)
        """
        # self.step is always zero, but the first step will be called via GET
        if self.step == 0 and request.method == 'GET':
            extra_context =  kwargs['extra_context']
            activity = extra_context.get('activity')
            bird = extra_context.get('bird')
            self.initial[(0)] = {
                'activity_content': activity.activity_content,
            }
        
        return super(close_experiment_wizard, self).__call__(request, *args, **kwargs)    

    def parse_params(self, request, *args, **kwargs):
        extra_context =  kwargs['extra_context']
        self.activity = extra_context.get('activity')
        self.form_list_orig = extra_context.get('form_list_orig')

    def get_template(self, step):
        return 'birdlist/basic/base_form_wizard.html'
        
    def render_template(self, request, form, previous_fields, step, context=None):
        
        context = context or {}
        # update the optional steps variable after each step so that the template
        # string get's displayed accordingly.
        if step == 2:
            self.extra_context['optional_steps'] = False
        else:
            self.extra_context['optional_steps'] = True
        
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


