from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.forms import URLInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contest, Story

class ContestForm(forms.ModelForm):
    class Meta:
       model = Contest
       fields = ["title", "description", "discussion_url", "max_in_group", "max_in_final", "max_votes", "min_text_size", "max_text_size", "starts", "submission_finishes", "voting_starts", "voting_starts_final", "finishes"]
       widgets = {
             "starts": DatePickerInput(),
             "submission_finishes": DatePickerInput(),
             "voting_starts": DatePickerInput(),
             "voting_starts_final": DatePickerInput(),
             "finishes": DatePickerInput(),
             "discussion_url": URLInput()
        }
    coordinator = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, label="Координатор")

class ContestCoordinatorForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ["theme", "theme_ext", "theme_by"]

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["title", "text", "contest"]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']

class VoteForm(forms.Form):
    vote1 = forms.ModelChoiceField(queryset=Story.objects.all(), label="1 место")
    vote2 = forms.ModelChoiceField(queryset=Story.objects.all(), label="2 место")
    vote3 = forms.ModelChoiceField(queryset=Story.objects.all(), label="3 место")
    vote4 = forms.ModelChoiceField(queryset=Story.objects.all(), label="4 место")
    vote5 = forms.ModelChoiceField(queryset=Story.objects.all(), label="5 место")
    vote6 = forms.ModelChoiceField(queryset=Story.objects.all(), label="6 место")