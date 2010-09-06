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
	url(r'^register_user/$', user_views.register_user),
	url(r'^login_user/$', user_views.login_user),
	url(r'^logout_user/$', 'django.contrib.auth.views.logout_then_login',
				{'login_url':'/colorific/login_user'}),
)

# Toolbox related pages
urlpatterns += patterns('',
     url(r'^tools/$','django.views.generic.list_detail.object_list',
                { 'queryset': Tool.objects.filter(active = True) }),
     url(r'^toolboxes/$', 'django.views.generic.list_detail.object_list',
                { 'queryset': ToolBox.objects.all() }),
     url(r'^toolboxes/(?P<toolbox_id>\d+)/$', toolbox_views.toolbox_detail),
     url(r'^create_toolbox/$', toolbox_views.create_toolbox),
     url(r'^edit_toolbox/(?P<toolbox_id>\d+)/$', toolbox_views.edit_toolbox),
	 url(r'^get_suggestions/$', toolbox_views.get_suggestions),
		
)



