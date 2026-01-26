from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django .forms.widgets import TextInput, PasswordInput
from django import forms
from .models import Comment, UserProfile
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.auth.forms import PasswordChangeForm

class registationForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"Username",'class': "form-control"}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder':"E-mail",'class': "form-control"}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder':"Password",'class': "form-control"}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder':"Confirm Password",'class': "form-control"}))
    first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"First Name",'class': "form-control"}))
    last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"Last Name",'class': "form-control"}))
    class Meta:
        model = User
        fields = ['email','username','password1','password2','first_name','last_name']

        
class loginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder':"Username",'class': "form-control"}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder':"Password",'class': "form-control"}))

class commentForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'rows':4, 'placeholder':"Add your comment...",}))
    class Meta:
        model = Comment
        fields = ['content']
class CustomDateInput(forms.DateInput):
    input_type = 'date'

class profileUpdateForm1(forms.ModelForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"Username",'class': "form-control"}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder':"E-mail",'class': "form-control"}))    
    first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"First Name",'class': "form-control"}))
    last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder':"Last Name",'class': "form-control"}))
    class Meta:
        model = User
        fields = ['email','username','first_name','last_name']

class profileUpdateForm2(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['gender','date_of_brith', 'phone_number','address','image_profile','short_message']
        widgets = {
            'date_of_brith': CustomDateInput(attrs={'class': 'form-control'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'image_profile': forms.FileInput(attrs={'class': 'form-control-image'}),
            'short_message' : forms.TextInput(attrs={'class': 'form-control'}), 
            }
        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a custom class to each input field
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})