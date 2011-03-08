from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from colorific.forms import RegistrationForm
from colorific.models import UserProfile

def about(request):
  return render_to_response('colorific/about.html',
        context_instance=RequestContext(request))
  
