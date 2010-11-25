from django.forms import ModelForm
from django import forms
from colorific.models import UserProfile, Tool, ToolBox, ToolBoxToolRelation, Image
from django.contrib.auth.models import User


class LoginForm(forms.Form):
		username = forms.CharField(max_length=30, label='Username')
		password = forms.CharField(max_length=20, widget=forms.PasswordInput(render_value=False))

# Note that a ModelForm includes a save()
class RegistrationForm(ModelForm):
	username = forms.CharField(max_length=30, label='Username')
	password = forms.CharField(max_length=20, widget=forms.PasswordInput(render_value=False))
	first_name =  forms.CharField( max_length=30)	
	email = forms.EmailField()
	
	def save(self):
		new_user = User.objects.create_user(username=self.cleaned_data['username'],
						    password=self.cleaned_data['password'],
						    email=self.cleaned_data['email'])
		new_user.first_name=self.cleaned_data['first_name']
		new_user.save()

		return new_user
		
	
	class Meta:
		model = UserProfile
		exclude  = ('user',)
		
	#Django's form system automatically looks for any method whose name
	#starts with clean_ and ends in the name of a form on the field,
	#then calls it after the field's built-in validation rules have
	#been applied
	'''def clean_username(self):
		try:
			#The attribute clean_data is a dictionary
			#of any submitted data that's made it through
			#validation so far
			User.objects.get(username=self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError("This username is already in use")
	'''
	#def clean(self):
	#	if 'password1' is self.cleaned_data and 'password2' is self.cleaned_data:
	#		raise forms.ValidationError("You must type the same password each time")
	#	return self.cleaned_data
	
# This is a simplified version of the edit form
# since a facebook user for example does not
# have to edit stuff here
class EditSocialUserForm(ModelForm):
		
	class Meta:
		model = UserProfile
		fields = ('tags',)

class EditUserForm(ModelForm):
	# user object fields
	username = forms.CharField(max_length=30, label='Username')
	password = forms.CharField(max_length=20, widget=forms.PasswordInput(render_value=False))
	first_name =  forms.CharField( max_length=30)	
	email = forms.EmailField()
	
	#user profile object fields
	tags = forms.CharField(max_length=200, help_text="Comma separated", required=False)
	
	class Meta:
		model = UserProfile
		exclude  = ('user',)
		
class ToolBoxForm (ModelForm):
	tools = forms.CharField(max_length=300,
		    help_text="Example: eclipse, firebug, screen, Ubuntu", widget=forms.TextInput(attrs={'size':'35'}))	
	class Meta:
		model = ToolBox
		exclude  = ('user', 'popularity',)
			

class EditToolForm(forms.Form):
	tool_name = forms.CharField(max_length=200, help_text="Eg. PyDev")
	toolnote_content = forms.CharField(max_length=300,
								  required=False,
		                          widget=forms.Textarea())	
	
class ToolForm(ModelForm):
	note = forms.CharField(max_length=300,
							  required=False,
	          				  widget=forms.Textarea(attrs={'class':'toolnoteContent'}),
	          		    	  help_text="How do you use this tool?",)	
	class Meta:
		model = ToolBoxToolRelation
	

class ImageForm(ModelForm):
	    class Meta:
	        model = Image
	    def __init__(self, user, *args, **kwargs):
					super(ImageForm, self).__init__(*args, **kwargs)
					self._user = user



			
			