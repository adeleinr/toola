from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from api.handlers import UserProfileHandler, AnonymousUserProfileHandler, ToolsHandler, ToolSuggestionsHandler, SearchSuggestionsHandler, SearchHandler, ToolboxesHandler

from django_piston_authentication import DjangoAuthentication

#auth = HttpBasicAuthentication(realm='My sample API')

auth = DjangoAuthentication()


#user_profile_resource = Resource(handler=AnonymousUserProfileHandler, authentication=auth) #Resource(AnonymousUserProfileHandler)
user_profile_resource = Resource(handler=AnonymousUserProfileHandler)
tools_resource = Resource(ToolsHandler)
tools_suggestions_resource = Resource(ToolSuggestionsHandler)
search_suggestions_resource = Resource(SearchSuggestionsHandler)
search_resource = Resource(SearchHandler)
toolboxes_resource = Resource(ToolboxesHandler)


urlpatterns = patterns('',
   url(r'^people/$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^people/(?P<userprofile_id>\d+)/$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^people/(?P<tag>\d+)/$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^people/(?P<limit>\d+)/$', user_profile_resource, { 'emitter_format': 'json' }),
   url(r'^tools/$', tools_resource, { 'emitter_format': 'json' }),
   url(r'^tools/(?P<toolbox_id>\d+)/(?P<tool_id>\d+)/$', tools_resource, { 'emitter_format': 'json' }),
   url(r'^tool_suggestions/$', tools_suggestions_resource, { 'emitter_format': 'json' }),
   url(r'^search_suggestions/$', search_suggestions_resource, { 'emitter_format': 'json' }),
   url(r'^search/$', search_resource, { 'emitter_format': 'json' }),
   url(r'^toolboxes/$', toolboxes_resource, { 'emitter_format': 'json' }),
   url(r'^toolboxes/(?P<toolbox_id>\d+)/$', toolboxes_resource),
   url(r'^toolboxes/(?P<username>\w+)/$', toolboxes_resource),
)
