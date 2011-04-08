from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from colorific.models import UserProfile, Tool, ToolBox, ToolBoxToolRelation
from webme.colorific.toolbox_views import get_all_toolboxes
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.utils import simplejson

# Used for Search Only
import haystack
from haystack.indexes import *
from haystack.query import SearchQuerySet

# List the users  => http://localhost:8084/api/people
# Get a user      => http://localhost:8084/api/people/1
# Get all users but this one  => http://localhost:8084/api/people/?exclude=1
# Get users, limit      => http://localhost:8084/api/people/?limit=3
# Get users, exclude and limit      => http://localhost:8084/api/people/?exclude=1&limit=3
# Get users, tag and limit      => http://localhost:8084/api/people/?tag=web-dev&limit=3
class UserProfileHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  model = UserProfile
  anonymous = 'AnonymousUserProfileHandler'
  fields = ('id', ('user', ('username', 'first_name')),
            'home_zipcode', 'absolute_url','absolute_public_url',
            'picture_url', 'picture_thumbnail', 'tags', 'pictures',)
  
  
  def read(self, request, userprofile_id = None):
    
    if userprofile_id:       
        try:
            userProfile = UserProfile.objects.get(pk = userprofile_id) 
            return userProfile
        except UserProfile.DoesNotExist:
            return rc.NOT_FOUND     
    else:    
      users = []
      if 'exclude' in request.GET:
        ''' Exclude one user only '''
        users = UserProfile.objects.exclude(pk = request.GET['exclude'])
        
      if 'tag' in request.GET:
        users = UserProfile.objects.filter(tags__slug__in=[request.GET['tag']])
    
      if not users:
        ''' Or get all users '''  
        users = UserProfile.objects.all()
        
      
      ''' Now truncate list if limit specified ''' 
      if 'limit' and users in request.GET: 
        limit = int(request.GET['limit'])
        users = users[:limit]  
      
  
  @classmethod
  def absolute_url(cls, myinstance):
    return myinstance.get_absolute_url()
  @classmethod
  def absolute_public_url(cls, myinstance):
    return myinstance.get_absolute_public_url()
  
  @classmethod
  def tags(cls, myinstance):
    return myinstance.tags.all()
  @classmethod
  def pictures(cls, myinstance):
    return myinstance.pictures.all()

# List the users  => http://localhost:8000/api/people
# Get a user      => http://localhost:8000/api/people/1
class AnonymousUserProfileHandler(UserProfileHandler, AnonymousBaseHandler):
  #fields = ('toolbox', 'id', ('user', ('username', 'first_name')),'home_zipcode', 'gender', 'occupation', 'self_description', 'twitter', 'absolute_url')
  fields = ('id', ('user', ('username', 'first_name')),
            'home_zipcode', 'absolute_url', 'absolute_public_url',
            'tags', ('pictures',()), 'picture_url', 'picture_thumbnail')   

# List the tools  => http://localhost:8084/api/tools
# Get a tool      => http://localhost:8084/api/tools/15/2003
# Create a tool   => curl -i -X POST -d "tool_name=mycooltool&toolbox_id=15" http://localhost:8084/api/tools
# Delete a tool   => curl -i -X DELETE  http://localhost:8084/api/tools/14/1
# Update a tool   => curl -i -X PUT -d "note=Testing api" http://localhst:8084/api/tools/15/2008/

class ToolsHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  model = ToolBoxToolRelation
  fields = ('id', ('tool', ('tool_name', 'tool_semantic_id', 'id', 'absolute_url', )), 'note', )
  
  @classmethod
  def absolute_url(cls, myinstance):
    return myinstance.get_absolute_url()
    
  def read(self, request, toolbox_id = None, tool_id = None):     
    if toolbox_id and tool_id:       
        try:
            toolBoxToolRelation = ToolBoxToolRelation.objects.get(toolbox = toolbox_id, 
                                                              tool = tool_id) 

            return toolBoxToolRelation
        except ToolBoxToolRelation.DoesNotExist:
            return rc.NOT_FOUND
    elif toolbox_id or tool_id:  
        return rc.NOT_FOUND
    else:
       #return Tool.objects.filter(active = True)
       return ToolBoxToolRelation.objects.all()
   
  def create(self, request):
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
    #tool.active = False
    tool.save()
    
    # We do remove the relationship entry
    toolBoxToolRelations = ToolBoxToolRelation.objects.filter(tool=tool_id, toolbox=toolbox_id)
    '''
    TODO
    print request.user
    if not request.user == toolBoxToolRelations[0].toolbox.user.id:
        return rc.FORBIDDEN # returns HTTP 401
    '''
    toolBoxToolRelations[0].delete()

    
    return rc.DELETED # returns HTTP 204
    
  
  def update(self, request, toolbox_id, tool_id):
    tool = Tool.objects.get(pk=tool_id) 
    toolBoxToolRelation = ToolBoxToolRelation.objects.get(toolbox = toolbox_id, 
                                                          tool = tool_id) 
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


# Get a suggestion for a tool => http://localhost:8084/api/tool_suggestions/?term=eclipse

class ToolSuggestionsHandler(BaseHandler):
  allowed_methods = ('GET')
  
  def read(self, request):
    response = ""
    term = request.GET['term'].lower()       
    result_list = []
    
    tools = Tool.objects.filter(tool_name__startswith=term)
    for tool in tools:
        tool_dict = { 'id': tool.id , "value":tool.tool_name }
        result_list.append(tool_dict)
    
    response = simplejson.dumps(result_list)
    return response
  
  
# Get a search suggestion for 
# a tool or toolbox => http://localhost:8084/api/search_suggestions/?term=eclipse
# Get a partial suggestion for
# a tool => http://localhost:8084/api/search_suggestions/?term=eclip
class SearchSuggestionsHandler(BaseHandler):
  allowed_methods = ('GET')
  
  def read(self, request):
    response = ""
    term = request.GET['term']
    result_list = [] 

    '''
      To filter more we do something like this:
      Eg. results = SearchQuerySet().models(ToolBox, Tool).filter(text__startswith=term).exclude(active=False)
    '''
    results = SearchQuerySet().models(ToolBox, ToolBoxToolRelation).filter(text__startswith=term)
    '''
    TODO use this limit? 
    limit = request.GET('limit')  
    if limit: 
        results = results[:int(limit)] 
    '''
    item_dict = {}

    for item in results:  
      if (isinstance(item.object, ToolBoxToolRelation)):
        item_dict = { 'id': item.object.toolbox.id , 'value':item.object.tool.tool_name, 'type': 'Tool','desc': item.object.toolbox.toolbox_name}
      elif (isinstance(item.object, ToolBox)):
        item_dict = { 'id': item.object.id , 'value':item.object.toolbox_name, 'type':'Toolbox', 'desc':''}
        
      result_list.append(item_dict)

    return result_list
  
# Search for tools or toolboxes
# => http://localhost:8084/api/search/?term=eclipse
class SearchHandler(BaseHandler):
  allowed_methods = ('GET')
  
  def read(self, request):
    response = ""
    term = request.GET['term']
    result_list = [] 
    
    results = SearchQuerySet().models(ToolBox, ToolBoxToolRelation).filter(text=term)
    
    item_dict = {}

    for item in results:  
       # If this a ToolBoxToolRelation object then
       # we need to grab the toolbox part of it
       # For some strange reason if we sent the whole 
       # ToolBoxToolRelation object to the template
       # engine it cannot access the toolbox object,
       # so we get it here
       if (isinstance(item.object, ToolBoxToolRelation)):
         result_list.append(item.object.toolbox)
       # Else this object is already a toolBox
       elif (isinstance(item.object, ToolBox)):
         result_list.append(item.object)

    return result_list

# List the toolboxes     => http://localhost:8084/api/toolboxes
# Get a toolbox          => http://localhost:8084/api/toolboxes/15
# Get a user's toolboxes => http://localhost:8084/api/toolboxes/adeleinr
# Create a toolbox   => curl -i -X POST -d "toolbox_name=Django%20Tools&
#                                           tools={%220%22:[%22Eclipse%22,%22/en/eclipse%22],%221%22:[%22Aptana%20IDE%22,%22/en/aptana_ide%22]}&
#                                           userprofile_id=1" http://localhost:8084/api/toolboxes
#                    => curl -i -X POST -H 'Content-Type: application/json' -d '{"toolbox_name": "mytoolbox", "userprofile_id":1, "tools": [{"tool_name": "test1", "note":"my note"},{"tool_name": "test2", "note":"my note"},{"tool_name": "test3", "note":"my note"}]}' http://localhost:8084/api/toolboxes
# Delete a toolbox   => curl -i -X DELETE  http://localhost:8084/api/toolboxes/14/
# Update a toolbox   => curl -i -X PUT -d "toolbox_name=New name" http://localhost:8084/api/toolboxes/15/    
class ToolboxesHandler(BaseHandler):
  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
  model = ToolBox
  fields = ('id', 'toolbox_name', 'popularity', 'absolute_url', ('user', ()), ('toolboxtoolrelations', ()),)
  
  def read(self, request, toolbox_id = None, username = None):     
    if toolbox_id:       
        try:
            toolBox = ToolBox.objects.get(pk = toolbox_id) 
            return toolBox
        except ToolBox.DoesNotExist:
            return rc.NOT_FOUND 
    elif username:
        try:
            toolBoxes = ToolBox.objects.filter(user__user__username = username).order_by('-pub_date')
            return toolBoxes
        except Exception:
            return rc.NOT_FOUND 
            
    else:
       return ToolBox.objects.all().order_by('-pub_date')
            
  def create(self, request):
    # This option is for when the input comes
    # structured like in JSON format for example
    if request.content_type:
      '''
        data = request.data

        userProfile = get_object_or_404(UserProfile, pk=data['userprofile_id'])
        
        toolBox = self.model(toolbox_name = data['toolbox_name'],
                             popularity = 0,
                             user = userProfile)
        toolBox.save()
                
        tools = simplejson.loads(data['tools'])
        
        for tool in data['tools']: 
            try:
              newTool = Tool.objects.get(tool_name=tool['tool_name'])
            except: 
              newTool = Tool.objects.create(tool_name=tool['tool_name'])

            # For now we are just recording that this
            # this tool has been used by someone everytime
            # TODO: need more efficient way to know if a tool
            # has been used or not
            #newTool.active = True
            #newTool.save()
            #toolBoxToolRelation = ToolBoxToolRelation.objects.create(toolbox = toolBox,
            #                                                          tool= newTool)  
          
        return rc.CREATED
        '''
    else:
      userProfile = get_object_or_404(UserProfile, pk=request.POST['userprofile_id'])

      toolBox = ToolBox.objects.create(toolbox_name = request.POST['toolbox_name'],
                                               popularity = 0,
                                               user = userProfile)
      tools = simplejson.loads(request.POST['tools'])
      
      
      # Tools list look like this:
      # [(u'1', [u'Aptana IDE', u'/en/aptana_ide']),
      # (u'0', [u'Eclipse', u'/en/eclipse'])]
      for _, value in tools.items():
        tool_name = value[0]
        tool_semantic_id = value[1]
        
        if not tool_name.isspace() and len(tool_name) > 0:
          try:
            newTool = Tool.objects.get(tool_name=tool_name, tool_semantic_id=tool_semantic_id)
          except: 
            try:
              if tool_name.isspace() or len(tool_name) <= 0:
                tool_semantic_id = 'noid'
              newTool = Tool.objects.create(tool_name=tool_name,tool_semantic_id = tool_semantic_id )
            except Exception, e:
              print e
              return rc.DUPLICATE_ENTRY
                   
            # For now we are just recording that
            # this tool has been used by someone every time
            # TODO: need to remove the active field
            newTool.active = True
            newTool.save()
 
          # toolBox.tools.add(newTool) -> Does not work
          # because we are specifying the 'though' table 
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
