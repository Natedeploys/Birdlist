from django.forms.widgets import TextInput
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

class TagAutocomplete(TextInput):
	
	def render(self, name, value, attrs=None):
		list_view = reverse('tagging_autocomplete-list')
		if not 'class' in attrs:
			attrs.update({'class' : 'vTextField'})
		html = super(TagAutocomplete, self).render(name, value, attrs)
		js = u'<script type="text/javascript">$(function() {installTaggingAutocompleate("%s", "%s") });</script>' % (attrs['id'], list_view)
		return mark_safe("\n".join([html, js]))
	
	class Media:
		# look for 'TAGGING_AUTOCOMPLETE_JS_BASE_URL' and 'TAGGING_AUTOCOMPLETE_CSS_BASE_URL'
		# in settings, otherwise use "'%sjquery-autocomplete' % settings.STATIC_URL"
		js_base_url = getattr(settings, 'TAGGING_AUTOCOMPLETE_JS_BASE_URL', '%sjquery-autocomplete' % settings.STATIC_URL)
		css_base_url = getattr(settings, 'TAGGING_AUTOCOMPLETE_CSS_BASE_URL', '%sjquery-autocomplete' % settings.STATIC_URL)
		
		css = {
                    'all': ('%s/smoothness/jquery-ui-1.8.7.custom.css' % css_base_url,)
                }
		js = (
		    '%s/jquery-1.4.4.min.js' % js_base_url,
		    '%s/jquery-ui-1.8.7.custom.min.js' % js_base_url,		    
			'%s/tagging_autocomplete.js' % js_base_url,
		)
