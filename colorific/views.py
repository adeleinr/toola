from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, RequestContext
from colorific.forms import RegistrationForm, LoginForm
from webme.colorific.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


#from demo import *

tools = {'e':['eclipse'],
         'a':['aptana'],
         'd':['delicious'],
         'g':['github']}


def get_suggestions(request):
    response = ""
    
    if request.method == 'GET':
        query = request.GET["q"]
        query = query.lower();
        first_char = query[:1]
        tool = tools.get(first_char)
        if tool:
            response = tool
        else:
            response = 'No suggestion'
    
    return HttpResponse(response,
      content_type="text")
    

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
                              { 'userProfile': user.get_profile(), 'user_count':user_count },
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
          return HttpResponseRedirect('/colorific/user_detail/'+request.user.username)
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
        
                            
                # Compute his/her demographic profile
                # Here we create a list of demographic variables
                # acquired from user and pass it to a function
                # that computes the demographic icon for the user
                # For now we are only caring about 2 ranges
                '''
                age_range = 2
                age = int(new_user_profile.age)
                if age >=25 and age <= 34:
                    age_range = 0
                elif age >=18 and age <= 24:
                    age_range = 1


                demographic_info = (age_range,
                                      new_user_profile.occupation,
                                      new_user_profile.gender,
                                      new_user_profile.ethnicity,
                                      new_user_profile.self_description)
                '''
                #new_user_profile.demographic_info = #computeDemo(demographic_info)
                new_user_profile.save()

                return HttpResponseRedirect('/colorific/user_detail/'+new_user.username, )
                
            except Exception, e:    
                    message = e
        else:
            #User needs to try again
            userForm = testUserForm
            message = 'Invalid form data'


    return render_to_response('colorific/register_user.html', {'userForm':userForm, 
                                'message':message}, 
                                 context_instance=RequestContext(request))


def show_demographic_info(request, username):
    
    return render_to_response('/colorific/show_demographic_info.html', {'demographic_color':demographic_color})

def create_toolbox(request):
    message = ''
    return render_to_response('colorific/create_toolbox.html', {'message':message}, 
                                 context_instance=RequestContext(request))
