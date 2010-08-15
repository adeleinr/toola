from django.forms import ModelForm
from django import forms
from colorific.models import UserProfile
from django.contrib.auth.models import User

AGE_RANGES = ('18-24', '25-34')

OCCUPATION_CHOICES = (
	(0, 'Tech Industry'),
	(1,'Student'),
  (2, 'My own business'),
	(3, 'At home'),
)


GENDER_CHOICES = (
	(0,'Male'),
	(1,'Female'),
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


class LoginForm(forms.Form):
		username = forms.CharField(max_length=30, label='Username')
		password = forms.CharField(max_length=20, widget=forms.PasswordInput(render_value=False))

# Note that a ModelForm includes a save()
class RegistrationForm(ModelForm):
	username = forms.CharField(max_length=30, label='Username')
	password = forms.CharField(max_length=20, widget=forms.PasswordInput(render_value=False))
	first_name =  forms.CharField( max_length=30 )	
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
		exclude  = ('user','demographic_description',)
		

	

      

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


