from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^colorific/',include('colorific.urls')),
    (r'^media_rsc/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media_rsc'}),	
)
