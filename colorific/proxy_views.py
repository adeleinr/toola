from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson
import urllib
from colorific.APIConfig import APIConfig
   
def toolbox(request):
  data = urllib.urlencode( {'toolbox_name' : request.GET['toolbox_name'],
                            'tools' : request.GET['tools'],
                            'userprofile_id' : request.GET['userprofile_id'] } )
  
  urllib.urlopen(APIConfig.TOOLBOX_API_URL, data).read() # HTTP POST Request

  # TODO: Read HTTP header from API
  json = simplejson.dumps({ 'result' : 'ok' })

  return HttpResponse(json, content_type="application/json")

def toolboxes(request):
  data = urllib.urlopen(APIConfig.TOOLBOX_API_URL).read() # HTTP GET Request

  # TODO: Read HTTP header from API
  json = simplejson.dumps(data)

  return HttpResponse(json, content_type="application/json")