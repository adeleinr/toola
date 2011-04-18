from django.db import models
from django import forms
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from sorl.thumbnail.fields import ImageWithThumbnailsField
import os

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
      
    #def get_pictures(self, num_pictures):
    #    return self.pictures.all().order_by('-id')[num_pictures]
    
    def get_pictures(self, num_pictures):
        return self.pictures.all().order_by('-id')[:num_pictures]
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
      
    def get_absolute_public_url(self):
        return "/colorific/people/%s" % (self.user.username)
    
    def absolute_url(self):
        return "/colorific/user_detail/%s" % (self.user.username)
      
    def absolute_public_url(self):
        return "/colorific/people/%s" % (self.user.username)


    
'''
   This class is used only for a profile (avatar) image
   If not a Social User (Ie. Facebook user) the
   ProfileImage class will upload the image in different
   sizes, so we use the large thumbnail format which is 200x200 pixels
   If a a Social User then his/her picture will
   be pulled from facebook and will be equivalent to this
   200x200 pixels picture               
'''
class ProfileImage(models.Model):
    def get_image_path(instance, filename):
      print "create path"
      val="uploads/images/avatars/" + str(instance.user.id)+"_"+filename
      print val
      return val 
    user = models.ForeignKey(UserProfile, editable=False, related_name='profile_picture')
    #picture = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    picture = ImageWithThumbnailsField(upload_to='uploads/images/avatars/',
                                       null=True, blank=True,
                                       thumbnail={'size': (50, 50), 'options': ('crop',)},
                                       extra_thumbnails={
                                                      'medium': {'size': (100, 100), 'options': ['crop', 'upscale']},
                                                      'large': {'size': (200, 400)},
                                       },
    )  
    

'''
  This class is used for all pictures associated with
  a user, except the profile picture
'''
class Image(models.Model):
    def get_image_path(instance, filename):
      print "create path"
      val="uploads/images/profiles/" + str(instance.user.id)+"_"+filename
      print val
      return val 
    user = models.ForeignKey(UserProfile, editable=False, related_name='pictures')
    #picture = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    picture = ImageWithThumbnailsField(upload_to='uploads/images/profiles/',
                                       null=True, blank=True,
                                       thumbnail={'size': (80, 80), 'options': ('crop',)},
                                       extra_thumbnails={
                                                      'medium': {'size': (100, 100), 'options': ['crop', 'upscale']},
                                                      'large': {'size': (200, 400)},
                                       },
    )
    
   
class Tool(models.Model):
    tool_name = models.CharField(max_length=150, help_text="Eg. PyDev")
    active = models.BooleanField()
    tool_semantic_id = models.CharField(blank=True, max_length=150)
    
    class Meta:    
      unique_together = (("tool_name", "tool_semantic_id"),)
    
    def __unicode__(self):
        return self.tool_name + " " + self.tool_semantic_id 

    def get_absolute_url(self):
        return "/colorific/tool/%s" % (self.tool_name)
    
    
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
    
