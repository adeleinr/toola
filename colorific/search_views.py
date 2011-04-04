from django.template import RequestContext
import haystack
from haystack.indexes import *
from haystack import site
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
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
  term= ''
  items = []
  
  if request.method == 'POST':
      term = request.POST.get('q')
      toolbox_id = request.POST.get('toolbox_id')
      
      print toolbox_id
      
      # If have information about the toolbox
      # it means the user used the search suggestion
      # to find a tool and the toolbox that contains it
      # So we retrieve this toolbox only
      if toolbox_id:
        url = "%s%s" % (APIConfig.TOOLBOX_API_URL, toolbox_id)
        print url
        res = urllib.urlopen(url)
        items.append(simplejson.load(res))
        
      # else we search for all the tool names
      # or toolboxes that contain this tool
      else: 
        url = "%s?term=%s" % (APIConfig.FULL_SEARCH_API_URL, term)
        res = urllib.urlopen(url)
        items = simplejson.load(res)
        
      return render_to_response('colorific/search.html',
                               {'message':message,
                                'items':items,
                                'term':term,
                               }, 
                               context_instance=RequestContext(request))
  else:     
    return HttpResponseRedirect('/colorific/toolboxes/')
       

          



  
