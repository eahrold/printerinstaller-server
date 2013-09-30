import os, sys
import site

#set the next line to your printerinstaller environment
PRINTERINSTALLER_ENV_DIR = '/path/to/your/printerinstaller_env/printerinstaller/'

# Use site to load the site-packages directory of our virtualenv
site.addsitedir(os.path.join(PRINTERINSTALLER_ENV_DIR, 'lib/python2.7/site-packages'))

# Make sure we have the virtualenv and the Django app itself added to our path
sys.path.append(PRINTERINSTALLER_ENV_DIR)
sys.path.append(os.path.join(PRINTERINSTALLER_ENV_DIR, 'printerinstaller'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'printerinstaller.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
