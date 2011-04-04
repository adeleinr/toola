#!/usr/bin/python
from django.conf import settings


class APIConfig:
  HOSTNAME = 'http://'+settings.HOSTNAME+':8084';
  USERPROFILE_API_URL = HOSTNAME+'/api/people/'
  TOOL_API_URL = HOSTNAME + '/api/tools/'
  TOOLBOX_API_URL = HOSTNAME + '/api/toolboxes/'
  ''' This URL is used for dropdown search suggestions '''
  SEARCH_API_URL = HOSTNAME + '/api/search_suggestions/'
  ''' This URL is used the actual search page '''
  FULL_SEARCH_API_URL = HOSTNAME + '/api/search/'
