from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, RequestContext
from colorific.forms import RegistrationForm, LoginForm, ToolBoxForm
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from webme.colorific.models import UserProfile, ToolBox, Tool, StaticTool
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


from django.utils import simplejson


def get_newest_toolbox(user):
    try:
        toolbox = ToolBox.objects.filter(user__user__username = user.username).latest('id')
        return toolbox;
    except: 
        return ''

def get_all_toolboxes(user):
    return ToolBox.objects.filter(user__user__username = user.username)


def get_suggestions(request):
    response = ""
    if request.method == 'GET':
        term = request.GET['term'].lower()       
        result_list = []
        
        tools = Tool.objects.filter(tool_name__startswith=term)
        for tool in tools:
            tool_dict = { 'id': tool.id , "value":tool.tool_name }
            result_list.append(tool_dict)
        
        response = simplejson.dumps(result_list)
      
    return HttpResponse(response, content_type="application/json")

   
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

    

@login_required(redirect_field_name='colorific/login_user')
# TODO: Need to find out how to pass the info from the ToolBoxForm
#       to the ToolBox object
def create_toolbox(request):
    message = ''
    user = request.user
    userProfile = user.get_profile()
    
    toolBoxForm = ToolBoxForm()
    if request.method == "POST":
        toolBoxForm = ToolBoxForm(request.POST)
        print toolBoxForm
        if toolBoxForm.is_valid():
            try:
                toolBoxForm.user = userProfile
                toolBox = ToolBox.objects.create(toolbox_name = request.POST['toolbox_name'],
                                                 user = userProfile)
                
                # Parse the comma separated tool names
                # and create tools from it
                # Then call 'add' to save to the relation
                # table
                for tool in request.POST['tools'].split(","):
                    tool = tool.rstrip().lstrip().lower()                  
                    if not tool.isspace():
                        try:
                            newTool = Tool.objects.get(tool_name=tool)
                        except: 
                            newTool = Tool.objects.create(tool_name=tool)
                            
                        toolBox.tools.add(newTool)

                message = 'success'
                toolBoxForm = ToolBoxForm()
                return render_to_response('colorific/create_toolbox.html',
                                   {'message':message,
                                    'toolBoxForm':toolBoxForm, 
                                    'toolBoxes':ToolBox.objects.filter(user__user__username = userProfile.user.username),
                                    'toolBox':get_newest_toolbox(userProfile.user)
                                   },
                                   context_instance=RequestContext(request))
            except Exception, e:    
                message = e
            # Do something.
        else:
            message = 'Invalid form data'
       
    
    return render_to_response('colorific/create_toolbox.html',
                               {'message':message,
                                'toolBoxForm':toolBoxForm,
                                'toolBoxes':ToolBox.objects.filter(user__user__username = userProfile.user.username),
                                'toolBox':get_newest_toolbox(userProfile.user)
                               }, 
                               context_instance=RequestContext(request))
    
def delete_toolbox(request):
    toolForm = ToolForm()
    message = ''
    return render_to_response('colorific/delete_toolbox.html', {'message':message,
                                                                'toolForm':toolForm}, 
                                 context_instance=RequestContext(request))
    
def delete_tool(request):
    message = ''
    return render_to_response('colorific/delete_tool.html', {'message':message},
                                 context_instance=RequestContext(request))
