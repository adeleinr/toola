from django.db import models
from django import forms
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class UserProfileLookupTables:
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

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    home_zipcode = models.CharField(max_length=5, blank=True)
    #gender = models.IntegerField(choices=UserProfileLookupTables.GENDER_CHOICES, blank=True)   
    #occupation = models.IntegerField('What do you do?', choices=UserProfileLookupTables.OCCUPATION_CHOICES, blank=True) 
    #self_description = models.IntegerField('Tag Yourself', choices=UserProfileLookupTables.SELF_DESC_CHOICES, blank=True)
    #twitter = models.URLField(verify_exists=True, max_length=200, blank=True)
    picture_url = models.URLField(max_length=200, blank=True)
    picture_thumbnail = models.URLField(max_length=200, blank=True)
    '''picture = models.ImageField(help_text=('Upload an image (max %s kilobytes)' %settings.MAX_PHOTO_UPLOAD_SIZE),
                                upload_to='jakido/avatar',blank=True, null= True)'''
    tags = TaggableManager()

    def get_home_zipcode(self):
        return self.home_zipcode
    '''
    def get_gender(self):
        return UserProfileLookupTables.GENDER_CHOICES[self.gender][1]

    def get_occupation(self):
        return UserProfileLookupTables.OCCUPATION_CHOICES[self.self_description][1]
                
    def get_self_description(self):
        return UserProfileLookupTables.SELF_DESC_CHOICES[self.self_description][1]
    
    def get_twitter_url(self):
        return self.twitter
    '''
    
    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return "/colorific/user_detail/%s" % (self.user.username)

   

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
    toolbox_name = models.CharField(max_length=100, help_text="Example: Django Setup.")
    user = models.ForeignKey(UserProfile)    
    tools = models.ManyToManyField(Tool,max_length=300, help_text="Eg. PyDev", through = 'ToolBoxToolRelation')
    popularity = models.PositiveIntegerField(blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'pub_date'

        
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
    toolbox = models.ForeignKey(ToolBox, related_name='toolboxtoolrelations')
    tool = models.ForeignKey(Tool)
    note = models.TextField(blank=True, max_length=350,)
    
    class Meta:
        unique_together = ('toolbox', 'tool')    
    
