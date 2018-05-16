#!/usr/bin/env python

# make sure to include the following directories which are not in the default
# python path by default
import sys
sys.path.append('../external_applications/')
sys.path.append('../internal_applications/')
sys.path.append('../../libraries/lib/python/')

# import platform dependent libraries
import platform
architecture = platform.machine()
sys.path.append('../../libraries/lib/python/%s' % architecture)

## original manage.py starts here
from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
