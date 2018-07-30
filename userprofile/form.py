from django import forms
from django.forms import ClearableFileInput
from .models import UserProfile

class UserProfileForm(forms.ModelForm, ClearableFileInput):
    template_with_initial = ''
    class Meta:
        model = UserProfile
        fields = ['photo','firstname','lastname']