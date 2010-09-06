from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext


def home(request):
    return render_to_response('colorific/home.html',
                              context_instance=RequestContext(request))