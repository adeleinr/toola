from django.conf.urls.defaults import *
#from tagging.models import Tool
from webme.colorific import main_views, user_views, toolbox_views
from webme.colorific.models import UserProfile, Tool, ToolBox

# General views
urlpatterns = patterns('',
  url(r'^$', main_views.home),
)

# User profile related pages
urlpatterns += patterns('',
  url(r'^people/$', user_views.users_index),
  url(r'^user_detail/(?P<username>[-\w]+)/$', user_views.user_detail),
  url(r'^login_user/$', user_views.login_user),
  url(r'^logout_user/$', 'django.contrib.auth.views.logout_then_login',
      {'login_url':'/colorific/login_user'}),
)

# Toolbox related pages
urlpatterns += patterns('',
  url(r'^tools/$', toolbox_views.tool_index),
  url(r'^toolboxes/$', toolbox_views.toolbox_index),
  url(r'^toolboxes/(?P<toolbox_id>\d+)/$', toolbox_views.toolbox_detail),
  url(r'^create_toolbox/$', toolbox_views.create_toolbox),
  url(r'^edit_toolbox/(?P<toolbox_id>\d+)/$', toolbox_views.edit_toolbox),
  url(r'^edit_tool/(?P<toolbox_id>\d+)/(?P<tool_id>\d+)/$', toolbox_views.edit_tool),
  url(r'^delete_tool/(?P<toolbox_id>\d+)/(?P<tool_id>\d+)/$', toolbox_views.delete_tool),
  url(r'^user_toolbox_list/$', toolbox_views.user_toolbox_index),
  url(r'^get_suggestions/$', toolbox_views.get_suggestions),
)