from django import forms
from .models import Note
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile
from cloudinary.forms import CloudinaryFileField
from markdownx.fields import MarkdownxFormField
from .models import Category

class NoteForm(forms.ModelForm):
    new_category = forms.CharField(required=False, label="Or create new")
    content =  MarkdownxFormField()
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(owner=user)

    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'due_date', 'is_pinned',  'new_category']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': '👤 Username',
            'email': '📧 Email Address'
        }

class ProfileImageForm(forms.ModelForm):
    image = CloudinaryFileField()
    class Meta:
        model = Profile
        fields = ['image']
        labels = {
            'image': '😊 picture'
        }