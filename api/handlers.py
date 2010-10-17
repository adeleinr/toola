from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from colorific.models import UserProfile, Tool, ToolBox, ToolBoxToolRelation
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.utils import simplejson

class UserProfileHandler(BaseHandler):
  
  model = UserProfile
  anonymous = 'AnonymousUserProfileHandler'
  fields = ('id', 'toolbox', ('user', ('username', 'first_name', 'password')),'home_zipcode', 'gender', 'occupation', 'self_description', 'twitter', 'absolute_url')
 
  @classmethod
  def gender(cls, myinstance):
    return myinstance.get_gender()

  @classmethod
  def occupation(cls, myinstance):
    return myinstance.get_occupation()

  @classmethod
  def self_description(cls, myinstance):
    return myinstance.get_self_description()

  @classmethod
  def absolute_url(cls, myinstance):
    return myinstance.get_absolute_url()

# List the users  => http://django:8000/api/people
# Get a user      => http://django:8000/api/people/1
class AnonymousUserProfileHandler(UserProfileHandler, AnonymousBaseHandler):
  fields = ('toolbox', 'id', ('user', ('username', 'first_name')),'home_zipcode', 'gender', 'occupation', 'self_description', 'twitter', 'absolute_url')
      

# List the tools  => http://django:8000/api/tools
# Get a tool      => http://django:8000/api/tools/15
# Create a tool   => curl -i -X POST -d "tool_name=mycooltool&toolbox_id=15" http://localhost:8084/api/tools
# Delete a tool   => curl -i -X DELETE  http://localhost:8084/api/tools/14/1
# Update a tool   => curl -i -X PUT -d "note=Testing api" http://localhst:8084/api/tools/15/2008/
class ToolsHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  model = Tool
  
  @classmethod
  def absolute_url(cls, myinstance):
    return myinstance.get_absolute_url()
    
  def read(self, request, toolbox_id = None, tool_id = None):     
    if toolbox_id and tool_id:       
        try:
            toolBoxToolRelation = ToolBoxToolRelation.objects.get(toolbox = toolbox_id, 
                                                              tool = tool_id) 
            # assuming obj is a model instance
            #from django.core import serializers
            #serialized_obj = serializers.serialize('json', [toolBoxToolRelation, ])

            return toolBoxToolRelation
        except ToolBoxToolRelation.DoesNotExist:
            return rc.NOT_FOUND
    elif toolbox_id or tool_id:  
        return rc.NOT_FOUND
    else:
       return Tool.objects.filter(active = True)
   
  def create(self, request):
    print request
    # This option is for when the input comes
    # structured like in JSON format for example
    if request.content_type:
        data = request.data    
        return rc.CREATED
    else:       
        try:
            toolbox = ToolBox.objects.get(pk=request.POST['toolbox_id'])
            try:
                tool = Tool.objects.create(tool_name=request.POST['tool_name'])
                toolBoxToolRelation = ToolBoxToolRelation.objects.create(toolbox = toolbox,
                                                                 tool= tool)
                tool.active = True
                tool.save()
                
                return rc.CREATED
            except IntegrityError:
                return rc.DUPLICATE_ENTRY

        except ToolBox.DoesNotExist:
            return rc.NOT_FOUND

    
  def delete(self, request, toolbox_id, tool_id):
    tool = Tool.objects.get(pk=tool_id)    
    # We do not want to remove this tool
    # once added it stays but we set it to
    # inactive
    tool.active = False
    tool.save()
    
    # We do remove the relationship entry
    toolBoxToolRelations = ToolBoxToolRelation.objects.filter(tool=tool_id, toolbox=toolbox_id)
    '''
    print request.user
    if not request.user == toolBoxToolRelations[0].toolbox.user.id:
        return rc.FORBIDDEN # returns HTTP 401
    '''
    toolBoxToolRelations[0].delete()

    
    return rc.DELETED # returns HTTP 204
    
  
  def update(self, request, toolbox_id, tool_id):
    print "hello1"
    tool = Tool.objects.get(pk=tool_id) 
    toolBoxToolRelation = ToolBoxToolRelation.objects.get(toolbox = toolbox_id, 
                                                          tool = tool_id) 
    print "hello1"
    toolBoxToolRelation.note = request.POST.get('note')
    
    
    # If the user is changing the name of the tool
    # we actually create a new tool and replace it in
    # the relation. This is because we want to keep all the
    # tools ever created.
    if request.PUT.get('tool_name') and tool.tool_name != request.PUT.get('tool_name'):
        tool.active = False
        # It is possible that a tool with the new name already exists
        newtool = Tool.objects.get_or_create(tool_name=request.POST['tool_name'])
        toolBoxToolRelation.tool = newtool
        return newtool
        

    tool.save()
    toolBoxToolRelation.save()
    return toolBoxToolRelation


# List the toolboxes => http://django:8000/api/toolboxes
# Get a toolbox      => http://django:8000/api/toolboxes/15
# Create a toolbox   => curl -i -X POST -d "toolbox_name=mytoolbox9&tools=tool1,tool2&userprofile_id=1" http://localhost:8084/api/toolboxes
#                    => curl -i -X POST -H 'Content-Type: application/json' -d '{"toolbox_name": "mytoolbox", "userprofile_id":1, "tools": [{"tool_name": "test1", "note":"my note"},{"tool_name": "test2", "note":"my note"},{"tool_name": "test3", "note":"my note"}]}' http://localhost:8084/api/toolboxes
# Delete a toolbox   => curl -i -X DELETE  http://localhost:8084/api/toolboxes/14/
# Update a toolbox   => curl -i -X PUT -d "toolbox_name=New name" http://localhost:8084/api/toolboxes/15/

class ToolboxesHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  model = ToolBox
  fields = ('id', 'toolbox_name', 'popularity', 'absolute_url', 'tools')
            
  def create(self, request):
    # This option is for when the input comes
    # structured like in JSON format for example
    if request.content_type:
        data = request.data

        userProfile = get_object_or_404(UserProfile, pk=data['userprofile_id'])
        
        toolBox = self.model(toolbox_name = data['toolbox_name'],
                             popularity = 0,
                             user = userProfile)
        toolBox.save()
                
        for tool in data['tools']: 
            try:
              newTool = Tool.objects.get(tool_name=tool['tool_name'])
            except: 
              newTool = Tool.objects.create(tool_name=tool['tool_name'])

            # For now we are just recording that this
            # this tool has been used by someone everytime
            # TODO: need more efficient way to know if a tool
            # has been used or not
            newTool.active = True
            newTool.save()
            toolBoxToolRelation = ToolBoxToolRelation.objects.create(toolbox = toolBox,
                                                                     tool= newTool)  
          
        return rc.CREATED
    else:
        userProfile = get_object_or_404(UserProfile, pk=request.POST['userprofile_id'])

        toolBox = ToolBox.objects.create(toolbox_name = request.POST['toolbox_name'],
                                                 popularity = 0,
                                                 user = userProfile)
        
        # Parse the comma separated tool names
        # and create tools from it
        # Then call 'add' to save to the relation
        # table
        print request.POST['tools']
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
                
        return rc.CREATED
                
        '''
        super(ExpressiveTestModel, self).create(request)'''


  def delete(self, request, toolbox_id):
    toolbox = ToolBox.objects.get(pk=toolbox_id)
    '''
    print request.user
    if not request.user == toolbox.user.user:
        return rc.FORBIDDEN # returns HTTP 401
    '''
    toolbox.delete()
    
    return rc.DELETED # returns HTTP 204
  
  def update(self, request, toolbox_id):
        toolbox =  toolbox = ToolBox.objects.get(pk=toolbox_id)        
        toolbox.toolbox_name = request.PUT.get('toolbox_name')
        toolbox.save()

        return toolbox
    
  @classmethod
  def absolute_url(cls, myinstance):
    return myinstance.get_absolute_url()