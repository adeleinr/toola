from django.conf.urls.defaults import *
#from tagging.models import Tool
from webme.colorific import views
from webme.colorific.models import UserProfile, Tool, ToolBox

urlpatterns = patterns('',
	url(r'^$', views.home),
	url(r'^people/$', views.users_index),
    url(r'^user_detail/(?P<username>[-\w]+)/$', views.user_detail),
	url(r'^register_user/$', views.register_user),
	url(r'^login_user/$', views.login_user),
	url(r'^logout_user/$', 'django.contrib.auth.views.logout_then_login',{'login_url':'/colorific/login_user'}),
	url(r'^create_toolbox/$', views.create_toolbox),
	url(r'^get_suggestions/$', views.get_suggestions),

)

urlpatterns += patterns('',
     url(r'^tools/$','django.views.generic.list_detail.object_list',
                { 'queryset': Tool.objects.all() }),
     url(r'^toolboxes/$', 'django.views.generic.list_detail.object_list',
                { 'queryset': ToolBox.objects.all() }),
		

)



