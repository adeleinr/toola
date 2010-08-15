from django.db import models
from django import forms
from tagging.fields import TagField, Tag
import tagging
from django.contrib.auth.models import User


AGE_RANGES = ('18-24', '25-34')

"""
OCCUPATION_CHOICES = (
    ('A Job', 'A Job'),
    ('My own business','My own business'),
    ('Engineer', 'Engineer'),
    ('Health Professional', 'Health Professional'),
    ('Teacher', 'Teacher'),
    ('Student', 'Student'),
    ('Parent at home', 'Parent at home'),
    ('My job moved to China', 'My job moved to China'),
    ('What job?', 'what job?'),

)
"""

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
    home_zipcode = models.CharField(max_length=5)
    gender = models.IntegerField(choices=GENDER_CHOICES)   
    occupation = models.IntegerField('What do you do?', choices=OCCUPATION_CHOICES) 
    self_description = models.IntegerField('Tag Yourself', choices=SELF_DESC_CHOICES)
    twitter = models.URLField(verify_exists=True, max_length=200, blank=True)

    
    #age = models.CharField(max_length=3)
    #work_zipcode = models.CharField(max_length=5 , blank=True)
    #ethnicity = models.IntegerField(choices=ETHNICITY_CHOICES)
    #demographic_info = models.CharField(max_length=10, blank=True)
    #facebook = models.URLField(verify_exists=True, max_length=200, blank=True)
    #flickr = models.URLField(verify_exists=True, max_length=200, blank=True)

    
    # If we call this field of the object we will get a string of
    # tags separated by space. To get a list of tags we need to set
    # a set and getting function as seen below.
    #tags_string = TagField(help_text="Separate tags with spaces.", blank=False)
        
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

    '''
    def get_age(self):
        return self.age
        
    def get_work_zipcode(self):
        return self.work_zipcode
        
    def get_facebook_url(self):
        return self.facebook
    
    def get_flickr_url(self):
        return self.flickr
    
    def _get_tags(self):
      return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)
        
    def get_ethnicity(self):
        return ETHNICITY_CHOICES[self.ethnicity][1]
        
    tags = property(_get_tags, _set_tags)
    '''    
      
    
'''try:
    tagging.register(UserProfile)
except tagging.AlreadyRegistered:
    pass
'''

class Tool(models.Model):
    
        def get_absolute_url(self):
            return "/colorific/user_detail/%s" % (self.user.username)
    