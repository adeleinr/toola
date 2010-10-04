from django.db import models
from django import forms
from django.contrib.auth.models import User


OCCUPATION_CHOICES = (
    (0, 'Tech Industry'),
    (1, 'Student'),
  (2, 'My own business'),
    (3, 'At home'),
    (3, 'At home'),
)

GENDER_CHOICES = (
    (0, 'Male'),
    (1, 'Female'),
)

SELF_DESC_CHOICES = (
    (0, 'Techie'),
    (1, 'College Life'),
    (2, 'Artsie'),
    (3, 'Nerd'),
    (4, 'Normal Human Being'),
     (5, 'Professional Traveler'),
    (6, 'Mystic'),
    (7, 'Health Sapient'),
    (8, 'Unknown'),
)

ETHNICITY_CHOICES = (
    (0, 'Hispanic'),
    (1, 'Asian'),
    (2, 'African American'),
    (3, 'Caucasian'),
)

class Task(models.Model):
    name = models.CharField(max_length=50)
    complete = models.BooleanField(default=False, null=False)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    home_zipcode = models.CharField(max_length=5)
    gender = models.IntegerField(choices=GENDER_CHOICES)   
    occupation = models.IntegerField('What do you do?', choices=OCCUPATION_CHOICES) 
    self_description = models.IntegerField('Tag Yourself', choices=SELF_DESC_CHOICES)
    twitter = models.URLField(verify_exists=True, max_length=200, blank=True)

        
    def get_self_description(self):
        return SELF_DESC_CHOICES[self.self_description][1]

    def get_home_zipcode(self):
        return self.home_zipcode
    
    def get_gender(self):
        return GENDER_CHOICES[self.gender][1]

    def get_occupation(self):
        return OCCUPATION_CHOICES[self.self_description][1]
    
    def get_twitter_url(self):
        return self.twitter
    
    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return "/colorific/user_detail/%s" % (self.user.username)



    
class StaticTool(models.Model):
    tool_name = models.CharField(max_length=100)   
    def __unicode__(self):
        return self.tool_name

    def get_absolute_url(self):
        return "/colorific/tool/%s" % (self.tool_name)
    

class Tool(models.Model):
    tool_name = models.CharField(unique=True, max_length=200, help_text="Eg. PyDev")
    active = models.BooleanField()
    
    #users = models.ManyToManyField(UserProfile)
    
    def __unicode__(self):
        return self.tool_name

    def get_absolute_url(self):
        return "/colorific/tool/%s" % (self.tool_name)
    
    
        
    '''
    def get_toolnote(self):
        return self.toolnote_set.all()[0]
    
    def get_toolnote_set(self):
        return self.toolnote_set.all()
    '''

''' 
    A ToolBox can have many Tools
    The same Tool could be used in many ToolBoxes 
    Tool is the granular thing
    ToolBox is the big thing
    Example
    -------
    p1 = Publication(id=None, title='The Python Journal')
    a1 = Article(id=None, headline='Django lets you build Web apps easily')
    a1.save()
    a1.publications.add(p1)
'''

    
class ToolBox(models.Model):
    toolbox_name = models.CharField(max_length=100, help_text="Eg. My Django Tools.")
    user = models.ForeignKey(UserProfile)    
    tools = models.ManyToManyField(Tool,max_length=300, help_text="Eg. PyDev", through = 'ToolBoxToolRelation')
    popularity = models.PositiveIntegerField(blank=True)
        
    def __unicode__(self):
        return self.toolbox_name
    
    def get_absolute_url(self):
        return "/colorific/toolboxes/%s" % (self.id)
    
    # Returns the relation entries for all the tools
    # in this toolbox by looking at the relation table,
    # not the toolbox table itself
    def get_toolbox_tools(self):
        return ToolBoxToolRelation.objects.filter(toolbox = self)

class ToolBoxToolRelation(models.Model):
    toolbox = models.ForeignKey(ToolBox)
    tool = models.ForeignKey(Tool)
    note = models.TextField(blank=True, max_length=350,)
    
    class Meta:
        unique_together = ('toolbox', 'tool')    
    

    