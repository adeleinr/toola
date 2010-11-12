import os
import sys
sys.path.append('/web/')
sys.path.append('/web/webme')

# put the Django project on sys.pat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webme.production_settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

