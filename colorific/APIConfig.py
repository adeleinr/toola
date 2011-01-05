#!/usr/bin/python
from django.conf import settings


class APIConfig:
  HOSTNAME = 'http://'+settings.HOSTNAME+':8084';
  USERPROFILE_API_URL = HOSTNAME+'/api/people/'
  TOOL_API_URL = HOSTNAME + '/api/tools/'
  TOOLBOX_API_URL = HOSTNAME + '/api/toolboxes/'
  SEARCH_API_URL = HOSTNAME + '/api/search_suggestions/'
  FULL_SEARCH_API_URL = HOSTNAME + '/api/search/'
