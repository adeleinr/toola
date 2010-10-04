from piston.handler import BaseHandler
from colorific.models import Task, UserProfile, Tool, ToolBox

# Create a task => curl -i -H "Accept: application/json" -X POST -d "name=do%20homework&complete=true" http://django:8000/api/task
# List the tasks => http://django:8000/api/tasks
class TaskHandler(BaseHandler):
  model = Task

# Create a task => curl -i -H "Accept: application/json" -X POST -d "user=pepe&home_zipcode=94089&gender=M&occupation=work&self_description=test&twitter=test.com" http://django:8000/api/people
# List the tasks => http://django:8000/api/people
class UserProfileHandler(BaseHandler):
  model = UserProfile
    
# Create a task => curl -i -H "Accept: application/json" -X POST -d "tool_name=php&active=true" http://django:8000/api/tools
# List the tasks => http://django:8000/api/tools
class ToolsHandler(BaseHandler):
  model = Tool

# List the tasks => http://django:8000/api/toolboxes
class ToolboxesHandler(BaseHandler):
  model = ToolBox