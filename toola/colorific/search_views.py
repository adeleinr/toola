from django.template import RequestContext
import haystack
from haystack.indexes import *
from haystack import site
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson
import urllib
from colorific.APIConfig import APIConfig
from colorific.models import ToolBox, Tool


'''
============================================================
===================   SEARCH VIEWS     ====================
============================================================
'''

def search(request):
  message = ''
  if request.method == 'GET':
      term = request.GET.get('q')
      url = "%s?term=%s" % (APIConfig.FULL_SEARCH_API_URL, term)
      res = urllib.urlopen(url)
      items = simplejson.load(res)

          
  return render_to_response('colorific/search.html',
                               {'message':message,
                                'items':items,
                                'term':term,
                               }, 
                               context_instance=RequestContext(request))


  
