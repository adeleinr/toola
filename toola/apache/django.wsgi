import os
import sys

'''
If you have been using the Django development server and have made use of the fact that it is possible when doing explicit imports, or when referencing modules in 'urls.py', to leave out the name of the site and use a relative module path, you will also need to add to sys.path the path to the site package directory itself
'''

sys.path.append('/web/webme/releases/current')
sys.path.append('/web/webme/releases/current/webme')

# put the Django project on sys.pat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webme.settings_production'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
