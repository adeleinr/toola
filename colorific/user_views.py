from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
import urllib, urllib2, base64

from colorific.models import UserProfile
from colorific.forms import RegistrationForm, LoginForm, ToolBoxForm
from colorific.toolbox_views import get_all_toolboxes
from colorific.APIConfig import APIConfig


   
def users_index(request):
  #print APIConfig.USERPROFILE_API_URL
            
  res = urllib.urlopen(APIConfig.USERPROFILE_API_URL)
  
  data = urllib.urlencode( {'toolbox_name' : 'mytoolbox9', 'tools' : 'tool1,tool2', 'userprofile_id' : 1 } )
  
  urllib.urlopen( 'http://django:8084/api/toolboxes', data).read()
  
  users = simplejson.load(res)
  
  return render_to_response('colorific/users_index.html',
                            { 'user_list': users},
                            context_instance=RequestContext(request))  

# TODO: Remove username from request
@login_required(redirect_field_name='colorific/login_user')

def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    userProfile = user.get_profile()
    user_count = UserProfile.objects.filter(self_description=userProfile.self_description).count()
    
    
    toolBoxForm = ToolBoxForm()
    
    return render_to_response('colorific/user_detail.html',
                              { 'userProfile': userProfile, 
                                'user_count': user_count,
                                'toolBoxes': get_all_toolboxes(user),
                                'toolBoxForm': toolBoxForm},
                                context_instance=RequestContext(request))

def login_user(request):
  
    loginForm = LoginForm()
    message = ''
    if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(username=username, password=password)
      
      if user is not None:
        if user.is_active:
          login(request, user)
          # Redirect to a success page
          return HttpResponseRedirect('/colorific/user_detail/' + username)
        else:
          message = 'Your account is disabled'
          
      else:
        message = 'Invalid login information'
        
      # Create a form with data to validate form
      testLoginForm = LoginForm(request.POST)
       
  
    return render_to_response('colorific/login_user.html', {'loginForm': loginForm, 
                'message':message}, context_instance=RequestContext(request))
    
  
def register_user(request):

    userForm = RegistrationForm()
    message = ''
    
    if request.method == 'POST':
        # Create a form with data to validate form
        testUserForm = RegistrationForm(request.POST)
    
        if testUserForm.is_valid():
            # Use the form data
            try:
                # Save user to db            
                new_user = testUserForm.save()
                new_user_profile = UserProfile.objects.create(user=new_user,
                                               home_zipcode = request.POST['home_zipcode'],
                                               gender = request.POST['gender'],
                                               occupation = request.POST['occupation'],
                                               self_description = request.POST['self_description'],
                                               twitter = request.POST['twitter'])

                new_user_profile.save()
                
                return HttpResponseRedirect('/colorific/user_detail/' + new_user.username)
                
            except Exception, e:    
                    message = e
        else:
            # User needs to try again
            userForm = testUserForm
            message = 'Invalid form data'


    return render_to_response('colorific/register_user.html', {'userForm':userForm,
                                                               'message':message}, 
                                 context_instance=RequestContext(request))

    

