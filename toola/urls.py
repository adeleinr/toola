from django.conf.urls.defaults import *
from django.conf import settings
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from colorific.models import ToolBox, Tool

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^api/',include('api.urls')),
    (r'^colorific/',include('colorific.urls')),
    (r'^media_rsc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media_rsc'}),
    (r'^socialregistration/',include('socialregistration.urls')),
    url(r'^search/', include('haystack.urls'),name='haystack_search'),
    
	
)

