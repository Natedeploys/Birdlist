import django.forms as forms

################################################################################
# pop-up addon
# see http://www.hoboes.com/Mimsy/?ART=675
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from songbird.settings import ADMIN_MEDIA_PREFIX

class SelectWithPop(forms.Select):
    def __init__(self, user=None, url = None, *args, **kwargs):
        super(SelectWithPop, self).__init__(*args, **kwargs)
        self.user = user
        self.url = url


    def render(self, name, *args, **kwargs):
        html = super(SelectWithPop, self).render(name, *args, **kwargs)

        # distinguish between given urls and once that we put together by doing
        # a reverse lookup
        if self.url == None:
            url = reverse('index_user', args=(self.user, ))
            field_name = name
        else:
            url = self.url
            field_name = ''

        field_id = name

        # "field_id" is always necessary - because the javascript code will use 
        # it to determine the field that has to be updated
        # "field_name" is used to create (parts of) the link - and is not 
        # always needed

        popupplus = render_to_string('widgets/popupplus.html', 
                    {'url': url, 'field': field_name, 'field_id': field_id, 
                    'ADMIN_MEDIA_PREFIX': ADMIN_MEDIA_PREFIX, })

        return html+popupplus

        
class MultipleSelectWithPop(forms.SelectMultiple):
    def __init__(self, user=None, *args, **kwargs):
        super(MultipleSelectWithPop, self).__init__(*args, **kwargs)
        self.user = user

    def render(self, name, *args, **kwargs):
        html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)

        url = reverse('index_user', args=(self.user, ))
        field_name = name
        field_id = name

        popupplus = render_to_string('widgets/popupplus.html', 
                    {'url': url, 'field': field_name, 'field_id': field_id, 
                    'ADMIN_MEDIA_PREFIX': ADMIN_MEDIA_PREFIX, })

        return html+popupplus

''' songbird specific adaptation of ajax_filtered_fields widget '''
import operator

from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ajax_filtered_fields import utils

''' function copied from ajax_filtered_fields.widget - could not import it '''
def _renderFilter(js_method_name, element_id, model, lookup_list, 
    select_related):
    """Return the html output of a filter link."""
    label, lookup_dict = lookup_list
    script = "ajax_filtered_fields.%s('%s', '%s', '%s', '%s', '%s')" % (
        js_method_name,
        element_id,
        model._meta.app_label, 
        model._meta.object_name, 
        utils.lookupToString(lookup_dict),
        select_related)
    return u"""
        <a class="ajax_filter_choice" 
            href="javascript:void(0)"
            onclick="%s">%s</a>
    """ % (script, label)

from django.forms.widgets import TextInput
#class FilteredSelectSimple(TextInput):
class FilteredSelectSimple(forms.Select):
    
    #def render(self, name, value, attrs=None):
    def render(self, name, value, attrs=None, choices=()):
        self._element_id = attrs['id']
        # choices links
        # if there is only one choice, then nothing will be rendered
        lookups_output = ""
        lookups = utils.getLookups(self.lookups)
        if len(lookups) > 1:
            js_method_name = "getForeignKeyJSON"
            lookups_output = "\n".join(
                _renderFilter(js_method_name, self._element_id, 
                    self.model, i, self.select_related) 
                for i in lookups)
                
        # get the selected object name
        selection = "-" * 9
        if value:
            selection = utils.getObject(self.model, {"pk": value}, 
                self.select_related)
        
        # filter selectbox input
        filter_id = "%s_input" % self._element_id
        
        # give a style to the final select widget
        _attrs = {"size": 2, "style": "width:270px;"}
        try:
            attrs.update(_attrs)
        except AttributeError:
            attrs = _attrs
            
        # normal widget output from the anchestor
        # create a field with a dummy name , the real value
        # will be retrieved from a hidden field
        parent_output = super(FilteredSelectSimple, self
            ).render("dummy-%s" % name, value, attrs, choices)
            #).render("dummy-%s" % name, value, attrs)            
        
        # output
        mapping = {
            "lookups_output": lookups_output,
            "selection": selection,
            "filter_id": filter_id,
            "parent_output": parent_output,
            "name": name,
            "element_id": self._element_id, 
            "value": "" if value is None else value,
            }
                            
        output = u"""
            <div class="selector">
                <div class="selector-available">
                    <p class="selector-filter" style="border:none;">
                        <input id="%(filter_id)s" type="text">
                    </p>
                    %(parent_output)s
                </div>
            </div>
            
            <input type="hidden" name="%(name)s" id="hidden-%(element_id)s" value="%(value)s" />
            
            <script type="text/javascript" charset="utf-8">
        		$(document).ready(function(){
                    SelectBox.init('%(element_id)s');

                    $("#%(filter_id)s").bind("keyup", function(e) {
                        SelectBox.filter("%(element_id)s", $("#%(filter_id)s").val())
                    });
                    
                    $(".ajax_letter").click(function(e) {
                        $("#%(filter_id)s").val("");
                    });
                    
                    ajax_filtered_fields.bindForeignKeyOptions("%(element_id)s");
        		});
        	</script>
            """ % mapping
            
        return mark_safe(output)
                
