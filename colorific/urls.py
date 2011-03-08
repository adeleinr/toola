from django.conf.urls.defaults import *
#from tagging.models import Tool
from webme.colorific import main_views, user_views, toolbox_views, proxy_views, search_views
from webme.colorific.models import UserProfile, Tool, ToolBox

# General views
urlpatterns = patterns('',
  url(r'^$', toolbox_views.toolbox_index),
  url(r'^about/$', main_views.about),
  
)

# User profile related pages
urlpatterns += patterns('',
  url(r'^people/$', user_views.users_index),
  url(r'^people/(?P<username>[-\w]+)/$', user_views.user_detail_public),
  url(r'^user_detail/$', user_views.user_detail2),
  url(r'^user_detail/(?P<username>[-\w]+)/$', user_views.user_detail),
  url(r'^signup_user/$', user_views.signup_user),
  url(r'^login_user/$', user_views.login_user),
  url(r'^logout_user/$', 'django.contrib.auth.views.logout_then_login',
      {'login_url':'/colorific/login_user'}),
  url(r'^edit_user/$', user_views.edit_user),
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
  url(r'^search/$', search_views.search),
)

# Toolbox proxies
urlpatterns += patterns('',
  url(r'^proxy/toolbox/$', proxy_views.toolbox),
  url(r'^proxy/toolboxes/$', proxy_views.toolboxes),
  url(r'^proxy/search_suggestions/$', proxy_views.search_suggestions)
)