from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contest, Story

class ContestForm(forms.ModelForm):
    class Meta:
       model = Contest
       fields = ["title", "description", "discussion_url", "max_in_group", "max_in_final", "max_votes", "min_text_size", "max_text_size", "starts", "submission_finishes", "voting_starts", "voting_starts_final"]

class ContestCoordinatorForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ["theme", "theme_by"]

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["title", "text"]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']