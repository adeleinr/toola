from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
import urllib, urllib2
from django.utils.functional import curry


from colorific.models import UserProfile, Image
from colorific.forms import RegistrationForm, LoginForm, ToolBoxForm, EditUserForm, EditSocialUserForm, ImageForm
from colorific.toolbox_views import get_all_toolboxes
from colorific.APIConfig import APIConfig


   
def users_index(request):           
  res = urllib.urlopen(APIConfig.USERPROFILE_API_URL)
  users = simplejson.load(res)
  
  return render_to_response('colorific/users_index.html',
                            { 'user_list': users},
                            context_instance=RequestContext(request))  


def user_detail_public(request, username):
   user = get_object_or_404(User, username=username)
   userProfile = user.get_profile()
  
   toolBoxForm = ToolBoxForm()
   
   similar_users = userProfile.tags.similar_objects()
   
     
   return render_to_response('colorific/user_detail_public.html',
                             { 'userProfile': userProfile, 
                               'toolboxes': get_all_toolboxes(userProfile.user.username),
                               'toolBoxForm': toolBoxForm,
                               'similar_users':similar_users},
                               context_instance=RequestContext(request))
   
# TODO: Remove username from request
@login_required(redirect_field_name='colorific/login_user')
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    userProfile = user.get_profile()
    
    if request.user.username != username:
      return HttpResponseRedirect(userProfile.get_absolute_public_url())
      
    #user_count = UserProfile.objects.filter(self_description=userProfile.self_description).count()
    user_count = 0

    toolBoxForm = ToolBoxForm()
    
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=1)

    ImageFormSet.form = staticmethod(curry(ImageForm, userProfile))
    
    formset = ImageFormSet(queryset=Image.objects.none())
    
    similar_users = userProfile.tags.similar_objects()
    
    if request.method == 'POST':
    
      if 'imageSubmit' in request.POST:
        
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if formset.is_valid():
          instances = formset.save(commit=False)
          for image in instances:
              try:
                 image.user = userProfile
                 image.save()
              except Image.DoesNotExist:
                 message = 'does not exit'
                 
 
    
    return render_to_response('colorific/user_detail.html',
                              { 'userProfile': userProfile, 
                                'user_count': user_count,
                                'toolboxes': get_all_toolboxes(userProfile.user.username),
                                'toolBoxForm': toolBoxForm,
                                'formset':formset,
                                'similar_users': similar_users},
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
  
@login_required(redirect_field_name='colorific/login_user')    
def edit_user(request):
  message = ''
  user = request.user
  userProfile = user.get_profile()
  
  if request.facebook:
      editUserForm = EditSocialUserForm(instance = userProfile)
  else:
      editUserForm = EditUserForm(instance = userProfile)
    
     
  if request.method == 'POST':
    
    if 'profileSubmit' in request.POST:
      # Create a form with data to validate form
      if request.facebook:
        editUserForm = EditSocialUserForm(request.POST, instance = userProfile)
      else:
        editUserForm = EditUserForm(request.POST, instance = userProfile)
   
      if editUserForm.is_valid():
          # Use the form data
        try:
          # Save user data
          editUserForm.save()
          
  
        except Exception, e:    
          message = e
      else:
          #User needs to try again)
          message = 'Invalid form data' 
  
  return render_to_response('colorific/edit_user.html', {'message': message, 'editUserForm': editUserForm,'userProfile':userProfile },
        context_instance=RequestContext(request))
    
