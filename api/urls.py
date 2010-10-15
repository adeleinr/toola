from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from api.handlers import TaskHandler, UserProfileHandler, AnonymousUserProfileHandler, ToolsHandler, ToolboxesHandler

from django_piston_authentication import DjangoAuthentication


#auth = HttpBasicAuthentication(realm='My sample API')

auth = DjangoAuthentication()



task_resource = Resource(TaskHandler)
#user_profile_resource = Resource(handler=AnonymousUserProfileHandler, authentication=auth) #Resource(AnonymousUserProfileHandler)
user_profile_resource = Resource(handler=AnonymousUserProfileHandler)
tools_resource = Resource(ToolsHandler)
toolboxes_resource = Resource(ToolboxesHandler)

urlpatterns = patterns('',
   url(r'^tasks$', task_resource, { 'emitter_format': 'json' }),
   url(r'^people$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^tools$', tools_resource, { 'emitter_format': 'json' }),
   url(r'^tools/(?P<toolbox_id>\d+)/(?P<tool_id>\d+)/$', tools_resource, { 'emitter_format': 'json' }),
   url(r'^toolboxes$', toolboxes_resource, { 'emitter_format': 'json' }),
   url(r'^toolboxes/(?P<id>.+)/$', toolboxes_resource),
)