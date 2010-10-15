import os
import sys
sys.path.append('/web/')
sys.path.append('/web/webme')

os.environ['DJANGO_SETTINGS_MODULE'] = 'webme.production_settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

