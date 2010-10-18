#!/usr/bin/python

class APIConfig:
  HOSTNAME = 'http://localhost:8084';
  USERPROFILE_API_URL = HOSTNAME+'/api/people'
  TOOL_API_URL = HOSTNAME + '/api/tools'
  TOOLBOX_API_URL = HOSTNAME + '/api/toolboxes'
