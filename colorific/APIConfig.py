#!/usr/bin/python
from django.conf import settings


class APIConfig:
  HOSTNAME = 'http://'+settings.HOSTNAME+':8084';
  print "hello ======================="+settings.HOSTNAME
  USERPROFILE_API_URL = HOSTNAME+'/api/people/'
  TOOL_API_URL = HOSTNAME + '/api/tools/'
  TOOLBOX_API_URL = HOSTNAME + '/api/toolboxes/'
