#!/usr/bin/python

from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME
from webme import settings

class DjangoAuthentication(object):
    """
    Django authentication. 
    """
    def __init__(self, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
        if not login_url:
            login_url = settings.LOGIN_URL
        self.login_url = login_url
        self.redirect_field_name = redirect_field_name
        self.request = None
    
    def is_authenticated(self, request):
        """
        This method call the `is_authenticated` method of django
        User in django.contrib.auth.models.
        
        `is_authenticated`: Will be called when checking for
        authentication. It returns True if the user is authenticated
        False otherwise.
        """
        print request.user.is_authenticated()
        self.request = request
        return request.user.is_authenticated()
        
    def challenge(self):
        """
        `challenge`: In cases where `is_authenticated` returns
        False, the result of this method will be returned.
        This will usually be a `HttpResponse` object with
        some kind of challenge headers and 401 code on it.
        """
        path = urlquote(self.request.get_full_path())
        tup = self.login_url, self.redirect_field_name, path 
        return HttpResponseRedirect('%s?%s=%s' %tup)