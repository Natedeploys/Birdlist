''' check if we are running on the django devel server or not 
	taken from: http://stackoverflow.com/questions/1291755/how-can-i-tell-whether-my-django-application-is-running-on-development-server-or/1291858#1291858
'''
def running_on_devserver(request):
	server = request.META.get('wsgi.file_wrapper', None)
	if server is not None and server.__module__ == 'django.core.servers.basehttp':
		return True
	else:
		return False		


def check_for_changed_model_fields(original_object, modified_object, appname, modelname):
    mods = {}

    # get the correct model
    from django.db.models import get_model
    model = get_model(appname, modelname)
    
    # see http://code.google.com/p/django-modelhistory/source/browse/branches/newhistory/utils.py?r=6
    from django.db.models import fields
    for field in model._meta.fields:
        #if not (isinstance(field, (fields.AutoField, fields.related.RelatedField))):
        # we usually want to keep track of RelatedFields too. however, we need
        # to lookup the values.
        if not (isinstance(field, (fields.AutoField, ))):
            orig_value = field.value_from_object(original_object)
            new_value = field.value_from_object(modified_object)
            
            # ignore GenericRelation
            if field.name in ['object_id', 'content_type']:
                continue
            
            ''' debug statements
            print field.name                
            print orig_value
            print new_value  '''
            if orig_value != new_value:
            
                orig_value_literal = ''
                new_value_literal = ''
                literal_value_present = False
                
                # In case we have a related field or IntegerField, we lookup the 
                # meaning / literal value of this field.
                # We might have to add more checks in the future.
                if isinstance(field, (fields.related.RelatedField, )):
                    literal_value_present = True
                    field_name = field.rel.to.__name__
                    field_module = field.rel.to.__module__
                    models_string = field_module.find('.models')
                    if models_string > 0:
                        field_module = field_module[0:models_string]
                    
                    model = get_model(field_module, field_name)
                    try:
                        orig_value_literal = model.objects.get(id = orig_value)
                        new_value_literal = model.objects.get(id = new_value)
                    except:
                        pass
                    
                elif isinstance(field, (fields.PositiveIntegerField, )):
                    literal_value_present = True
                    choices = field.choices
                    try:
                        orig_value_literal = choices[orig_value][1]
                        new_value_literal = choices[new_value][1]
                    except:
                        pass                        
                        
                
                mods[field.name] = (orig_value, new_value, field.verbose_name, 
                                    literal_value_present, 
                                    orig_value_literal, new_value_literal)
    
    return mods


def print_changed_activity_fields(mods):
    for key in mods.iterkeys():
        print key + " (" + str(mods[key][2]) + ") changed from '" +  str(mods[key][0]) + "' to '" + str(mods[key][1]) + "'"
        #if mods[key][3]:
            #print str(mods[key][4]) + " changed to " + str(mods[key][5])


