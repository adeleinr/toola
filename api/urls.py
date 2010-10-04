from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import TaskHandler, UserProfileHandler, ToolsHandler, ToolboxesHandler

task_resource = Resource(TaskHandler)
user_profile_resource = Resource(UserProfileHandler)
tools_resource = Resource(ToolsHandler)
toolboxes_resource = Resource(ToolboxesHandler)

urlpatterns = patterns('',
   url(r'^tasks$', task_resource, { 'emitter_format': 'json' }),
   url(r'^people$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^tools$', tools_resource, { 'emitter_format': 'json' }),
   url(r'^toolboxes$', toolboxes_resource, { 'emitter_format': 'json' }),
)