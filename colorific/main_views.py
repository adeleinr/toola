from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from colorific.forms import RegistrationForm
from colorific.models import UserProfile

def about(request):
  return render_to_response('colorific/about.html',
        context_instance=RequestContext(request))
  
def home(request):
  userForm = RegistrationForm()
  message = ''
  user = request.user
      
  if user is not None and user.is_authenticated():
      return HttpResponseRedirect('/colorific/user_detail/'  + user.username)
    
  else:
   
    if request.method == 'POST':
          # Create a form with data to validate form
          testUserForm = RegistrationForm(request.POST)
            
          if testUserForm.is_valid():
              # Use the form data
            try:
                  # Save user to db            
                  new_user = testUserForm.save()
                  
                  '''
                  new_user_profile = UserProfile.objects.create(user=new_user,
                                                 home_zipcode = request.POST['home_zipcode'],
                                                 gender = request.POST['gender'],
                                                 occupation = request.POST['occupation'],
                                                 self_description = request.POST['self_description'],
                                                 twitter = request.POST['twitter'])
                  '''
                  new_user_profile = UserProfile.objects.create(user=new_user,
                                     home_zipcode = request.POST['home_zipcode'])

                  user = authenticate(username=request.POST['username'], password=request.POST['password'])
                  login(request, user)
                  
                  return HttpResponseRedirect('/colorific/user_detail/'  + user.username)
            except Exception, e:    
                      message = e
          else:
              #User needs to try again
              userForm = testUserForm
              message = 'Invalid form data' 
  
  return render_to_response('colorific/home.html', {'message': message, 'userForm': userForm },
        context_instance=RequestContext(request))