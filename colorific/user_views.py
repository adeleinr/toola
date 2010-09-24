from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from colorific.models import UserProfile
from colorific.forms import RegistrationForm, LoginForm
from colorific.toolbox_views import get_all_toolboxes
   
def home(request):
    return render_to_response('colorific/home.html',
                              context_instance=RequestContext(request))
def users_index(request):
    return render_to_response('colorific/users_index.html',
                              { 'user_list': UserProfile.objects.all()},
                              context_instance=RequestContext(request))

@login_required(redirect_field_name='colorific/login_user')
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    userProfile = user.get_profile()
    user_count = UserProfile.objects.filter(self_description=userProfile.self_description).count()  
    return render_to_response('colorific/user_detail.html',
                              { 'userProfile': user.get_profile(), 
                                'user_count':user_count,
                                'toolBoxes': get_all_toolboxes(user)},
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
          return HttpResponseRedirect('/colorific/create_toolbox/')
        else:
          message = 'Your account is disables'
          
      else:
        message = 'Invalid login information'
        
      # Create a form with data to validate form
      testLoginForm = LoginForm(request.POST)
       
  
    return render_to_response('colorific/login_user.html', {'loginForm':loginForm, 
                'message':message}, context_instance=RequestContext(request))
    
  
def register_user(request):

    userForm = RegistrationForm()
    message = ''
    
    if request.method == 'POST':
        # Create a form with data to validate form
        testUserForm = RegistrationForm(request.POST)
        print testUserForm 
    
        if testUserForm.is_valid():
            # Use the form data
            try:
                # Save user to db            
                new_user = testUserForm.save()
                print testUserForm['home_zipcode']
                new_user_profile = UserProfile.objects.create(user=new_user,
                                               home_zipcode = request.POST['home_zipcode'],
                                               gender = request.POST['gender'],
                                               occupation = request.POST['occupation'],
                                               self_description = request.POST['self_description'],
                                               twitter = request.POST['twitter'])

                new_user_profile.save()

                return HttpResponseRedirect('/colorific/user_detail/', )
                
            except Exception, e:    
                    message = e
        else:
            #User needs to try again
            userForm = testUserForm
            message = 'Invalid form data'


    return render_to_response('colorific/register_user.html', {'userForm':userForm,
                                                               'message':message}, 
                                 context_instance=RequestContext(request))

    

