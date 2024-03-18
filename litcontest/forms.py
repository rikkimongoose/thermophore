from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ContestForm(forms.Form):
    title = forms.CharField(max_length=200, label="Название конкурса")
    description = forms.CharField(widget=forms.Textarea, label="Описание конкурса")
    discussion_url = forms.CharField(max_length=256, label="Ссылка на страницу с обсуждением конкурса")
    max_in_group = forms.IntegerField(label="Максимальное количество произведений в группе")
    max_in_final = forms.IntegerField(label="Максимальное количество произведений в финале")
    max_votes = forms.IntegerField(label="Количество произведений, за которые голосует участник (1-6)")
    min_text_size = forms.IntegerField(label="Минимальная длина произведения (без лимита: 0)")
    max_text_size = forms.IntegerField(label="Максимальная длина произведения (без лимита: 0)")
    starts = forms.DateField(label="Дата объявления темы и начала приема работ")
    submission_finishes = forms.DateField(label="Дата окончания приема работ")
    voting_starts = forms.DateField(label="Дата начала первого тура")
    voting_starts_final = forms.DateField(label="Дата окончания первого тура")
    finishes = forms.DateField(label="Дата окончания конкурса")

class ContestCoordinatorForm(forms.Form):
    theme = forms.CharField(max_length=200, label="Ссылка на страницу с обсуждением конкурса")
    theme_by = forms.CharField(max_length=200, label="Ссылка на страницу с обсуждением конкурса")

class StoryForm(forms.Form):
    title = forms.CharField(max_length=200, label="Название")
    text = forms.CharField(widget=forms.Textarea, label="Текст")

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']