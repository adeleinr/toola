from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.utils import simplejson
import urllib, urllib2


from colorific.forms import ToolBoxForm, ToolForm
from colorific.models import UserProfile, ToolBox, Tool, ToolBoxToolRelation
from colorific.APIConfig import APIConfig


'''
============================================================
===================   TOOLBOX VIEWS     ====================
============================================================
'''

def toolbox_index(request):
  res = urllib.urlopen(APIConfig.TOOLBOX_API_URL)
  toolboxes = simplejson.load(res)
  return render_to_response('colorific/toolbox_index.html',
                            { 'toolboxes': toolboxes},
                            context_instance=RequestContext(request)) 
  
def get_all_toolboxes(username):
    res = urllib2.urlopen(APIConfig.TOOLBOX_API_URL+str(username))
    toolboxes = simplejson.load(res)
    return toolboxes

#TODO not used yet
def get_toolbox_popularity(request, toolbox_id):
    toolbox = get_object_or_404(ToolBox, pk=toolbox_id)
    return render_to_response('colorific/toolbox_detail.html', {'toolBoxPopularity': toolbox.popularity}, 
                              context_instance=RequestContext(request))

def toolbox_detail(request, toolbox_id):
    res = urllib.urlopen(APIConfig.TOOLBOX_API_URL+str(toolbox_id))
    toolbox = simplejson.load(res)
    return render_to_response('colorific/toolbox_detail.html', {'toolbox': toolbox}, 
                              context_instance=RequestContext(request))

def get_newest_toolbox(user):
    try:
        toolbox = ToolBox.objects.filter(user__user__username = user.username).latest()
        return toolbox;
    except: 
        return ''


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

@login_required(redirect_field_name='colorific/login_user')
# TODO: Need to find out how to pass the info from the ToolBoxForm
#       to the ToolBox object
def create_toolbox(request):
    message = ''
    user = request.user
    userProfile = user.get_profile()
    newest_toolBox = get_newest_toolbox(userProfile.user)
    
    toolBoxForm = ToolBoxForm()
    if request.method == "POST":
        toolBoxForm = ToolBoxForm(request.POST)
        print toolBoxForm
        if toolBoxForm.is_valid():
            try:
                toolBoxForm.user = userProfile
                toolBox = ToolBox.objects.create(toolbox_name = request.POST['toolbox_name'],
                                                 popularity = 0,
                                                 user = userProfile)
                
                # Parse the comma separated tool names
                # and create tools from it
                # Then call 'add' to save to the relation
                # table
                for tool in request.POST['tools'].split(","):
                    tool = tool.rstrip().lstrip().lower()                  
                    if not tool.isspace() and len(tool) > 0:
                        try:
                            newTool = Tool.objects.get(tool_name=tool)
                        except: 
                            newTool = Tool.objects.create(tool_name=tool)
                            
                        # For now we are just recording that this
                        # this tool has been used by someone everytime
                        # TODO: need more efficient way to know if a tool
                        # has been used or not
                        newTool.active = True
                        newTool.save()
                        
                        # We cant do this because we are specifying the
                        # 'though' table 
                        # toolBox.tools.add(newTool) -> Does not work
                        # Instead we need to create every relation entry
                        toolBoxToolRelation = ToolBoxToolRelation.objects.create(toolbox = toolBox,
                                                                                 tool= newTool)
                        

                message = 'success'
 
                return HttpResponseRedirect('/colorific/create_toolbox')
                
            except Exception, e:    
                message = e
            # Do something.
        else:
            message = 'Invalid form data'
        
    return render_to_response('colorific/create_toolbox.html',
                               {'message':message,
                                'toolBoxForm':toolBoxForm,
                                'toolBoxes':ToolBox.objects.filter(user__user__username = userProfile.user.username)[:5],
                                'toolBox':newest_toolBox,
                                'userProfile':userProfile
                               }, 
                               context_instance=RequestContext(request))
    
@login_required(redirect_field_name='colorific/login_user')
def user_toolbox_index(request):
    user = request.user
    userProfile = user.get_profile()
    return render_to_response('colorific/user_toolbox_list.html', 
                              {'toolboxes':get_all_toolboxes(userProfile.user.username)},
                              context_instance=RequestContext(request))


@login_required(redirect_field_name='colorific/login_user')
def edit_toolbox(request, toolbox_id):
    
    message = ''
    #Get toolbox if it exists
    toolBox = get_object_or_404(ToolBox, pk=toolbox_id)
    
    #Get user from session
    user = request.user
    userProfile = user.get_profile()
    
    #Check that this users owns this toolbox
    if toolBox.user.id ==  userProfile.id:
        return render_to_response('colorific/edit_toolbox.html', {'toolBox': toolBox}, 
                              context_instance=RequestContext(request))
          
    else:
        message = 'You do not own this toolbox'
        return render_to_response('colorific/edit_toolbox.html',
                               {'message':message,
                               }, 
                               context_instance=RequestContext(request))

# TODO No used yet
def delete_toolbox(request):
    toolForm = ToolForm()
    message = ''
    return render_to_response('/colorific/delete_toolbox.html', {'message':message,
                                                                'toolForm':toolForm}, 
                                 context_instance=RequestContext(request))
    

'''
============================================================
===================   TOOLS VIEWS     ======================
============================================================
'''

def tool_index(request):
  res = urllib.urlopen(APIConfig.TOOL_API_URL)
  tools = simplejson.load(res)
  return render_to_response('colorific/tool_index.html',
                            { 'tools': tools},
                            context_instance=RequestContext(request)) 

@login_required(redirect_field_name='colorific/login_user')
def edit_tool(request, toolbox_id, tool_id):
    message = ''
    #Get tool if it exists
    tool = get_object_or_404(Tool, pk=tool_id)
    toolBoxToolRelation = get_object_or_404(ToolBoxToolRelation,
                                            toolbox = toolbox_id, 
                                            tool = tool_id)
    #Get user from session
    user = request.user
    userProfile = user.get_profile()
        
    if request.method == "POST":
      
      toolForm = ToolForm(request.POST, instance=toolBoxToolRelation)        
      if toolForm.is_valid():
        toolForm.save()
        toolForm = ToolForm(instance=toolBoxToolRelation)
        message = "Success"   
    
    else:
      toolForm = ToolForm(instance=toolBoxToolRelation)    
    
    return render_to_response('colorific/edit_tool.html',
                                 {'message':message,
                                  'toolForm':toolForm,
                                  'toolBoxToolRelation':toolBoxToolRelation,
                                 }, 
                                 context_instance=RequestContext(request))
             
    

#TODO Since this is a GET we need to confirm if the user
# wants to delete. Or else we would need to change this to be a POST
@login_required(redirect_field_name='colorific/login_user')
def delete_tool(request, toolbox_id, tool_id):
    tool = get_object_or_404(Tool, pk=tool_id)
    #if request.method == 'POST':
    toolBoxToolRelations = ToolBoxToolRelation.objects.filter(tool=tool_id, toolbox=toolbox_id)
    if toolBoxToolRelations[0].toolbox.user.id == request.user.id:
            toolBoxToolRelations[0].delete()
            return HttpResponseRedirect('/colorific/edit_toolbox/'+str(toolbox_id))
        
    '''
    else:
        
        return HttpResponseRedirect('/colorific/edit_tool/'+str(toolbox_id)+'/'+str(tool_id))
    '''

